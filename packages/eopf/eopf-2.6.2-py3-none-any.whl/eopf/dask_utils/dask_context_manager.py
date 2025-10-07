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
dask_context_manager.py

Dask context manager implementation

"""
import importlib
import math
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional, Union

import cloudpickle
import dask.config
import distributed
import psutil
from dask.distributed import Client
from dask.system import CPU_COUNT
from dask.utils import parse_bytes
from distributed import LocalCluster, get_client, performance_report
from importlib_metadata import PackageNotFoundError

from eopf.common import functions_utils
from eopf.dask_utils import auto_gc_plugin, failure_monitor_plugin
from eopf.dask_utils.auto_gc_plugin import AutoGCPlugin
from eopf.dask_utils.dask_cluster_type import ClusterType
from eopf.dask_utils.dask_helpers import wait_for_workers
from eopf.dask_utils.failure_monitor_plugin import FailureMonitorPlugin
from eopf.exceptions import TriggeringConfigurationError
from eopf.exceptions.errors import DaskClusterNotFound, DaskClusterTimeout, TimeOutError
from eopf.logging.log import EOLogging

if TYPE_CHECKING:
    pass

# https://github.com/dask/distributed/issues/8695

cloudpickle.register_pickle_by_value(auto_gc_plugin)
cloudpickle.register_pickle_by_value(failure_monitor_plugin)


class DaskContext:
    """
    Representation of a dask context used to run
    dask with the correct configuration in a context manager

    Parameters
    ----------
    cluster_type: type of cluster to use
        can be one of:

            * **None**: don't create a new cluster, just connect to one
            * **local**: configure a :py:class:`~dask.distributed.LocalCluster`
            * **ssh**: configure a :py:func:`~dask.distributed.SSHCluster`
            * **kubernetes**: configure a :py:class:`~dask_kubernetes.KubeCluster`
            * **pbs**: configure a :py:class:`~dask_jobqueue.PBSCluster`
            * **sge**: configure a :py:class:`~dask_jobqueue.SGECluster`
            * **lsf**: configure a :py:class:`~dask_jobqueue.LSFCluster`
            * **slurm**: configure a :py:class:`~dask_jobqueue.SLURMCluster`
            * **slurm**: configure a :py:class:`~dask_jobqueue.SLURMCluster`
            * **yarn**: configure a :py:class:`~dask_yarn.YarnCluster`
            * **gateway**: configure a :py:class:`~dask_gateway.GatewayCluster`
            * **address**: to pass simple cluster address in the addr parameter
            * **custom**: to use Custom cluster class specified by following element in **cluster_config** element.

                - **module**: python path to module containing custom cluster
                - **cluster**: cluster class name
    address: str
        only for **str** cluster_type, specified cluster address to join.
    cluster_config: dict
        key value pairs of parameters to give to the cluster constructor
    client_config: dict
        element to configure :py:class:`~dask.distributed.Client`
    performance_report_file : Optional[str]
        path to report file
    """

    def __init__(
        self,
        cluster_type: Optional[ClusterType] = None,
        *,
        address: Optional[str] = None,
        cluster_config: Optional[dict[str, Any]] = None,
        client_config: Optional[dict[str, Any]] = None,
        dask_config: Optional[dict[str, Any]] = None,
        performance_report_file: Optional[Union[str, Path]] = None,
    ) -> None:
        self._cluster_type: Optional[ClusterType] = cluster_type
        self._cluster: Optional[Any] = None
        self._logger = EOLogging().get_logger("eopf.dask_utils.dask_context_manager")
        self._client: Optional[Client] = None
        self._performance_report_file = performance_report_file
        self._performance_report: Optional[performance_report] = None
        # See https://distributed.dask.org/en/latest/diagnosing-performance.html
        if self._performance_report_file:
            self._performance_report = performance_report(filename=self._performance_report_file)
            self._logger.info(f"Performance report file requested : {self._performance_report_file}")

        self._client_config: dict[str, Any] = client_config if client_config else {}
        self._cluster_config: dict[str, Any] = cluster_config if cluster_config else {}
        self._dask_config: dict[str, Any] = dask_config if dask_config else {}
        self._dask_config_set: Optional[dask.config.set] = None
        self._minimum_workers: int = 0
        self._logger.info(
            f"Initialising an {cluster_type} cluster with client conf : {self._client_config} "
            f",cluster config {self._cluster_config} and dask config {self._dask_config}",
        )

        # detect any other client, this might cause conflict on the cluster
        self._detect_existing_client()

        # need to setup dask config before instance clusters and so on
        if len(self._dask_config) != 0:
            self._logger.debug(f"Setting dask config : {self._dask_config}")
            self._dask_config_set = dask.config.set(self._dask_config)
            self._dask_config_set.__enter__()

        if address is not None and "address" not in self._client_config:
            warnings.warn(
                "Address on dask context is deprecated, use clusterType.ADDRESS with address in client_config",
            )
            self._client_config["address"] = address

        setup_dict: dict[ClusterType | None, Callable[[], None]] = {
            ClusterType.LOCAL: self._setup_local_cluster,
            ClusterType.SSH: self._setup_ssh_cluster,
            ClusterType.KUBERNETES: self._setup_kubernetes_cluster,
            ClusterType.PBS: self._setup_pbs_cluster,
            ClusterType.SGE: self._setup_sge_cluster,
            ClusterType.LSF: self._setup_lsf_cluster,
            ClusterType.SLURM: self._setup_slurm_cluster,
            ClusterType.YARN: self._setup_yarn_cluster,
            ClusterType.GATEWAY: self._setup_gateway_cluster,
            ClusterType.ADDRESS: self._setup_address_cluster,
            ClusterType.CUSTOM: self._setup_custom_cluster,
            None: self._setup_none_cluster,
        }

        # setup cluster
        if self._cluster_type not in setup_dict:
            raise TriggeringConfigurationError("Unhandled dask context cluster type")
        # Setup the cluster
        setup_dict[self._cluster_type]()

        self._logger.info(f"DASK Cluster : {str(self._cluster)}")

    def _detect_existing_client(self) -> None:
        """
        Detect any other client as this might cause conflict on the cluster

        For we keep going with a warning

        Returns
        -------

        """
        try:
            client = get_client()
            # if a client exist log its infos
            if client is not None:
                self._logger.warning(
                    f"A Dask client is already active: {id(client)} : {client}"
                    f", creating a new one can result in"
                    f"strange behaviour",
                )
        except ValueError:
            self._logger.debug("No Dask client active, proceeding")

    def _setup_none_cluster(self) -> None:
        # No cluster type provided try address
        self._cluster_type = ClusterType.ADDRESS
        self._setup_address_cluster()

    def _setup_address_cluster(self) -> None:
        if "address" not in self._client_config:
            raise TriggeringConfigurationError(
                "address parameter or in client config is mandatory for STR cluster connexion",
            )

    def _setup_yarn_cluster(self) -> None:
        try:
            from dask_yarn import YarnCluster  # pylint: disable=import-outside-toplevel

            self._cluster = YarnCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_yarn should be installed.") from exc

    def _setup_slurm_cluster(self) -> None:
        try:
            from dask_jobqueue import (
                SLURMCluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = SLURMCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.") from exc

    def _setup_lsf_cluster(self) -> None:
        try:
            from dask_jobqueue import (
                LSFCluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = LSFCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.") from exc

    def _setup_sge_cluster(self) -> None:
        try:
            from dask_jobqueue import (
                SGECluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = SGECluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.") from exc

    def _setup_pbs_cluster(self) -> None:
        try:
            from dask_jobqueue import (
                PBSCluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = PBSCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_jobqueue should be installed.") from exc

    def _setup_kubernetes_cluster(self) -> None:
        try:
            from dask_kubernetes import (
                KubeCluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = KubeCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_kubernetes should be installed.") from exc

    def _setup_ssh_cluster(self) -> None:
        try:
            from dask.distributed import (
                SSHCluster,  # pylint: disable=import-outside-toplevel
            )

            self._cluster = SSHCluster(**self._cluster_config)
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask distributed ssh should be installed.") from exc

    def _setup_local_cluster(self) -> None:
        """
        Starts a local cluster. Options from dask documentation
        https://distributed.dask.org/en/latest/api.html#distributed.LocalCluster:
        name=None, n_workers=None, memory_limit: str, float, int, or None, default “auto”,
        threads_per_worker=None, processes=None, loop=None, start=None, host=None,
        ip=None, scheduler_port=0, silence_logs=30, dashboard_address=':8787', worker_dashboard_address=None,
        diagnostics_port=None, services=None, worker_services=None, service_kwargs=None, asynchronous=False,
        security=None, protocol=None, blocked_handlers=None, interface=None, worker_class=None,
        scheduler_kwargs=None, scheduler_sync_interval=1, **worker_kwargs

        """
        self.__compute_local_n_workers()
        self._minimum_workers = self._cluster_config.get("n_workers", 0)
        self._cluster = LocalCluster(**self._cluster_config)

    def __compute_local_n_workers(self) -> None:
        """
        Compute the local workers to use depending on parameters
        Particularly if you want a memory driven cluster size, dask doesn't provide this feature
        If you already provides a n_worker parameter the minimum between possible and your number will be set

        Warnings
        --------
        - Memory limit as per Dask documentation is worker wise. This means that threads_per_worker shares it.


        Returns
        -------
        None, the _cluster_config is filled instead

        """
        if "memory_limit" in self._cluster_config and isinstance(self._cluster_config["memory_limit"], str):
            # Compute the overall possible number of worker possible on the machine
            available_memory = round(psutil.virtual_memory().available / (1024**3))
            memory_limit_gb = parse_bytes(self._cluster_config["memory_limit"]) / (1024**3)
            nb_possible_workers = min(math.floor(available_memory / memory_limit_gb), CPU_COUNT)
            n_workers = min(nb_possible_workers, self._cluster_config.get("n_workers", CPU_COUNT))
            # Minimum one worker
            n_workers = max(n_workers, 1)
            self._cluster_config["n_workers"] = n_workers

    def _setup_custom_cluster(self) -> None:
        module_name: str = "NotFound"
        try:
            module_name = self._cluster_config.pop("module")
            cluster_class_name = self._cluster_config.pop("cluster")
            cluster = getattr(importlib.import_module(module_name), cluster_class_name)(
                **self._cluster_config,
            )
            self._cluster = cluster
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                f"Module {module_name} not found, corresponding package should be installed",
            ) from exc

    def _setup_gateway_cluster(self) -> None:
        try:
            from dask_gateway import Gateway  # pylint: disable=import-outside-toplevel
            from dask_gateway.auth import (
                get_auth,  # pylint: disable=import-outside-toplevel
            )
            from dask_gateway.client import (
                ClusterStatus,  # pylint: disable=import-outside-toplevel
            )

            # setup gateway Auth
            # one of ("kerberos", "jupŷterhub", "basic") or a python pass to the auth class
            if "auth" in self._cluster_config:
                auth_kwargs = self._cluster_config.pop("auth")
                dask.config.set(gateway__auth__kwargs=auth_kwargs)
                auth_type = auth_kwargs.pop("type", None)
                auth = get_auth(auth_type)
            else:
                auth = None
            # Number of workers
            n_workers: Optional[int | dict[str, Any]] = self._cluster_config.pop("n_workers", None)
            # setup gateway
            gateway_url = self._cluster_config.pop("address")
            gateway = Gateway(address=gateway_url, auth=auth)
            # reuse existing cluster ?
            previous_cluster_name: Optional[str] = self._cluster_config.pop("reuse_cluster", None)
            wait_timeout: int = self._cluster_config.pop("connect_timeout", 60)
            if previous_cluster_name is not None:
                available_clusters = [
                    cluster.name for cluster in gateway.list_clusters() if cluster.status == ClusterStatus.RUNNING
                ]
                if previous_cluster_name in available_clusters:
                    self._logger.info(f"Reusing previous cluster {previous_cluster_name}")
                    self._logger.debug(
                        f"Previous cluster status page : {gateway_url}/clusters/{previous_cluster_name}/status",
                    )
                    try:
                        cluster = functions_utils.run_with_timeout(
                            gateway.connect,
                            timeout=wait_timeout,
                            cluster_name=previous_cluster_name,
                            **self._cluster_config,
                        )
                    except TimeOutError as exc:
                        raise DaskClusterTimeout(
                            f"Connecting to Dask Gateway cluster {previous_cluster_name} "
                            f"timed out after {wait_timeout} seconds.",
                        ) from exc
                else:
                    raise DaskClusterNotFound(
                        f"Previous cluster not found on the gateway : {previous_cluster_name}, "
                        f"available : {available_clusters}",
                    )
            else:
                self._logger.info(f"Creating new cluster with config {self._cluster_config}")
                try:
                    cluster = functions_utils.run_with_timeout(
                        gateway.new_cluster,
                        **self._cluster_config,
                        timeout=wait_timeout,
                    )
                except TimeOutError as exc:
                    raise DaskClusterTimeout(
                        f"Creating a new cluster " f"timed out after {wait_timeout} seconds.",
                    ) from exc
            # scale the cluster
            if n_workers is not None:
                self._scale_gateway_cluster(cluster, n_workers)
            self._cluster = cluster
        except ModuleNotFoundError as exc:
            raise PackageNotFoundError("Package dask_gateway should be installed.") from exc

    def _scale_gateway_cluster(
        self,
        cluster: distributed.SpecCluster,
        n_workers: int | dict[str, Any],
    ) -> None:
        """
        Scale a cluster

        Parameters
        ----------
        cluster: cluster to scale
        n_workers ; int or dict["minimum" : ..., "maximum":...[,"active" : ...]]

        Returns
        -------

        """
        if isinstance(n_workers, int):
            cluster.scale(n_workers)
            self._minimum_workers = n_workers
        elif isinstance(n_workers, dict):
            cluster.adapt(
                minimum=n_workers["minimum"],
                maximum=n_workers["maximum"],
                active=n_workers.get("active", True),
            )
            self._minimum_workers = n_workers["minimum"]

    def __del__(self) -> None:
        """
        Destructor to clean resources

        Returns
        -------

        """
        if self._client is not None:
            self._client.close()
        if self._cluster is not None:
            self._cluster.close()
        if self._dask_config_set is not None:
            self._dask_config_set.__exit__(None, None, None)
        self._cluster = None
        self._client = None
        self._dask_config_set = None
        self._performance_report = None

    def __enter__(self) -> "DaskContext":
        """
        Context manager enter

        Returns
        -------

        """
        self._logger.debug("Starting dask client and cluster")

        if self._cluster is not None:
            self._cluster.__enter__()
            self._logger.debug(f"Starting dask cluster : {id(self._cluster)}")
            self._client = Client(address=self._cluster, **self._client_config)
        else:
            self._logger.debug(f"No cluster created at init(), using Client({self._client_config})")
            self._client = Client(**self._client_config)
        # Initiate client
        self._logger.info(f"Dask Client : {str(self._client)}")
        self._logger.debug(f"Starting dask client : {id(self._client)}")
        self._client.register_plugin(FailureMonitorPlugin(), name="failure-monitor")
        self._client.register_plugin(AutoGCPlugin(), name="auto-gc")
        self._client.__enter__()
        self._logger.info(f"Dask dashboard address: {self._client.dashboard_link}")
        # Wait for the minimum workers to be available:
        wait_workers: bool = self._cluster_config.pop("wait_for_workers", True)
        wait_timeout: int = self._cluster_config.pop("wait_timeout", 999)
        wait_raises: bool = self._cluster_config.pop("wait_raises", True)
        if wait_workers:
            self._logger.info(f"Waiting for {self._minimum_workers} workers to be ready")
            try:
                wait_for_workers(self._minimum_workers, timeout=wait_timeout)
            except DaskClusterTimeout:
                self._logger.warning("Minimum number of worker not reached !")
                if wait_raises:
                    raise

        if self._performance_report:
            self._performance_report.__enter__()
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """
        Context manager exit

        Parameters
        ----------
        args
        kwargs

        Returns
        -------

        """
        self._logger.debug(f"Stopping dask client and cluster {self}")
        if self._performance_report:
            try:
                self._performance_report.__exit__(*args, **kwargs)
            except RecursionError:
                self._logger.error(
                    "Well known dask recursion error in performance report writing, skipping the generation",
                )

        if self._client is not None:
            self._logger.debug(f"Stopping dask client : {id(self._client)}")
            self._logger.debug(f"processing : {self._client.processing()}")
            self._client.__exit__(*args, **kwargs)

        if self._cluster is not None:
            self._logger.debug(f"Stopping dask cluster : {id(self._cluster)}")
            self._cluster.__exit__(*args, **kwargs)

        if self._dask_config_set is not None:
            self._dask_config_set.__exit__(*args, **kwargs)

        self._client = None
        self._cluster = None
        self._dask_config_set = None

    @property
    def cluster(self) -> Any:
        """
        Get the cluster

        Returns
        -------

        """
        if self._cluster is None:
            raise ValueError("No dask cluster !!!")
        return self._cluster

    @property
    def client(self) -> Client:
        """
        Get the client

        Returns
        -------

        """
        if self._client is None:
            raise ValueError("No dask client !!!")
        return self._client

    def __str__(self) -> str:
        return f"cluster : {self.cluster}, client : {self.client}"
