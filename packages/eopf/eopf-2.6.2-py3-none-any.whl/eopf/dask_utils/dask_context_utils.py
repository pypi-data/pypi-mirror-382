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
dask_context_utils.py

Utility functions for dask context creation

"""
from functools import wraps
from typing import Any, Callable

from eopf import EOConfiguration, EOLogging
from eopf.dask_utils import ClusterType, DaskContext

EOConfiguration().register_requested_parameter(
    "dask_context__cluster_type",
    param_is_optional=True,
    description="Dask cluster type to use in init_from_eo_configuration",
)

EOConfiguration().register_requested_parameter(
    "dask_context__performance_report_file",
    param_is_optional=True,
    description="Dask performance file to use in init_from_eo_configuration",
)


def init_from_eo_configuration() -> DaskContext:
    """
    Init a Dask Context using EOConfiguration parameters

    Returns
    -------
    A dask context, default to local cluster if no configuration is provided

    """
    conf = EOConfiguration()
    # init defaults
    cluster_config = {}
    auth_config = {}
    client_config = {}
    performance_report_file = None
    address = None

    try:
        cluster_type_str = conf.dask_context__cluster_type
        cluster_type = ClusterType(cluster_type_str)
    except KeyError:
        cluster_type = None

    if cluster_type == ClusterType.ADDRESS:
        if not conf.has_value("dask_context__addr"):
            raise KeyError("missing dask_context__addr in EOConfiguration for ADDRESS cluster")
        address = conf.dask_context__addr

    for c in conf.param_list_available:
        if c.startswith("dask_context__cluster_config__"):
            if c.startswith("dask_context__cluster_config__auth__"):
                auth_config[c.replace("dask_context__cluster_config__auth__", "")] = getattr(conf, c)
                continue
            cluster_config[c.replace("dask_context__cluster_config__", "")] = getattr(conf, c)
        elif c.startswith("dask_context__client_config__"):
            client_config[c.replace("dask_context__client_config__", "")] = getattr(conf, c)
        elif c == "dask_context__performance_report_file":
            performance_report_file = getattr(conf, c)

    if len(auth_config) > 0:
        cluster_config["auth"] = auth_config

    return DaskContext(
        address=address,
        cluster_type=cluster_type,
        client_config=client_config,
        cluster_config=cluster_config,
        performance_report_file=performance_report_file,
    )


def remote_dask_cluster_decorator(config: dict[Any, Any]) -> Any:
    """Wrapper function used to setup a remote dask cluster and run the wrapped function on it

    Parameters
    ----------
    config: Dict
        dictionary with dask cluster configuration parameters

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    >>> dask_config = {
    ...    "cluster_type": "gateway",
    ...    "cluster_config": {
    ...        "address": "http://xxx.xxx.xxx.xxx/services/dask-gateway",
    ...        "auth": {
    ...            "auth": "jupyterhub",
    ...            "api_token": "xxxxxxxxxxxxxx"
    ...        },
    ...        "image": "registry.eopf.copernicus.eu/cpm/eopf-cpm:feat-create-docker-image",
    ...        "worker_memory": 4,
    ...        "n_workers" : 8
    ...    },
    ...    "client_config": {
    ...        "timeout" : "320s"
    ...    }
    ... }
    ...
    >>> @remote_dask_cluster_decorator(dask_config)
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    """
    logger = EOLogging().get_logger("eopf.dask_utils.dask_utils")

    def wrap_outer(fn: Callable[[Any, Any], Any]) -> Any:
        @wraps(fn)
        def wrap_inner(*args: Any, **kwargs: Any) -> Any:
            with DaskContext(
                cluster_type=ClusterType.GATEWAY,
                cluster_config=config["cluster_config"],
                client_config=config["client_config"],
            ) as ctx:  # noqa
                if ctx.client is not None:
                    logger.info(f"Dask dashboard address: {ctx.client.dashboard_link}")
                return fn(*args, **kwargs)

        return wrap_inner

    return wrap_outer
