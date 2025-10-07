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
dask_logging.py

dask logging utilities
"""

import logging.config
from typing import TYPE_CHECKING, Any

import dask.config
from distributed.config import initialize_logging

from eopf import EOLogging

if TYPE_CHECKING:  # pragma: no cover
    from distributed.client import Client

DEFAULT_FMT: str = (
    "%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : "
    "(Process Details : (%(process)d, %(processName)s), "
    "Thread Details : (%(thread)d, %(threadName)s))\nLog : %(message)s"
)


def configure_dask_logging(cluster_type: Any, logging_config: dict[str, Any], default_fmt: str = DEFAULT_FMT) -> None:
    """
    Configure the dask loggers

    Parameters
    ----------
    cluster_type
    logging_config
    default_fmt

    Returns
    -------

    """
    if cluster_type is not None:
        distributed_config = {"distributed": {"logging": logging_config}}
        if "version" not in logging_config:
            distributed_config["distributed"].setdefault("admin", {})["log-format"] = logging_config.pop(
                "distributed.admin.log-format",
                default_fmt,
            )
        dask.config.set({"distributed.logging": logging_config})
        initialize_logging(distributed_config)
    else:
        logging.config.dictConfig(logging_config)


def print_dask_client_cluster_info(client: "Client") -> None:
    """
    Print dask cluster infos
    Parameters
    ----------
    client

    Returns
    -------

    """
    logger = EOLogging().get_logger("eopf.dask_utils")
    if client is not None:
        # If a client exists, print information about the scheduler and workers
        scheduler_info = client.scheduler_info()
        logger.info("Dask Cluster Information:")
        logger.info("=========================")
        logger.info("Scheduler:")
        logger.info(scheduler_info["address"])

        for worker, worker_info in scheduler_info["workers"].items():
            logger.info(f"Worker: {worker}")
            logger.info(f"Worker info: {worker_info}")
