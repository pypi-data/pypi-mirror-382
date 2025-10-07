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
dask_helpers.py

Dask computation tools

"""
import gc
import time
from asyncio import CancelledError
from typing import Any, Optional

import dask
from dask.array import Array
from distributed import Client, Future, as_completed, get_client

from eopf.common.file_utils import AnyPath
from eopf.config.config import EOConfiguration
from eopf.exceptions.errors import DaskClusterTimeout, DaskComputingError
from eopf.logging.log import EOLogging

EOConfiguration().register_requested_parameter(
    "dask_utils__compute__step",
    9999,
    True,
    description="Number of dask future computed simultaneously in dask_utils",
)

EOConfiguration().register_requested_parameter(
    "dask_utils__timeout",
    300,
    True,
    description="Default timeout on a submitted task",
)

EOConfiguration().register_requested_parameter(
    "dask_utils__retries",
    3,
    True,
    description="Default number of retries",
)


class FutureLike:
    """Simulates a Dask Future when no distributed client exists."""

    def __init__(self, value: Any) -> None:
        self.value = value

    def result(self, timeout: Optional[int] = None) -> Any:
        """Returns the computed result immediately."""
        return self.value

    def done(self) -> bool:
        """A FakeFuture is always 'done' since it's computed synchronously."""
        return True

    def cancel(self) -> bool:
        """Mimic cancel method (does nothing here)."""
        return False

    def exception(self) -> None:
        """No exception handling needed for immediate computation."""
        return None

    def __repr__(self) -> str:
        return f"FutureLike({self.value})"


def compute(*args: Any, **kwargs: Any) -> list[FutureLike | Future]:
    """
    Custom compute function that checks if a Dask client is available.
    If a client is available, it uses client.compute.
    Otherwise, it falls back to dask.compute and provides FutureLike object mimicking the future api
    """
    # Check if a Dask client is already instantiated
    logger = EOLogging().get_logger("eopf.dask_utils.dask_utils")
    collection = args[0] if isinstance(args[0], (list, tuple)) else [args[0]]
    client = get_distributed_client()
    priority = kwargs.pop("priority", 0)
    if client is None:
        logger.debug("Computing without client ")
        return [FutureLike(v) for v in dask.compute(collection, **kwargs)]
    logger.debug(f"Computing using client {id(client)}")
    logger.debug(f"Sending {collection} to the client with priority {priority}")
    return client.compute(
        collection,
        priority=priority,
        retries=kwargs.pop("retries", EOConfiguration()["dask_utils__retries"]),
        **kwargs,
    )


def wait_and_get_results(
    futures: list[FutureLike | Future],
    cancel_at_first_error: Optional[bool] = True,
    **kwargs: Any,
) -> list[Any]:
    """
    Function to wait on the futures list and return the results.
    Order is kept.
    FutureLike objects are accepted

    """

    indexed_futures = dict(
        enumerate(futures),
    )  # Store index-future mapping to return the results in the same order as input
    results = [None] * len(futures)  # Pre-allocate results list
    real_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, Future)}
    fake_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, FutureLike)}
    # No real found
    if len(real_futures) != 0:
        client = get_distributed_client()
        if client is None:
            raise DaskComputingError("Dask future computation requested but no Client available !!!!")
        _wait_and_get_results_dask(client, real_futures, results, cancel_at_first_error, **kwargs)

    # Process FakeFutures (already done in essence)
    for index, future in fake_futures.items():
        results[index] = future.result()
        gc.collect()

    return results  # Returns results in correct order


def _wait_and_get_results_dask(
    client: Client,
    real_futures: dict[int, Future],
    results: list[Any],
    cancel_at_first_error: Optional[bool] = True,
    **kwargs: Any,
) -> None:
    """
    Wait and get result on real dask futures

    Parameters
    ----------
    real_futures : dict[idx, futures] index is kept to return results in the same order as input
    results : results to fill
    cancel_at_first_error : Cancel everything at first error
    kwargs : Any kwars ( timeout etc)

    Returns
    -------
    None as results is filled
    """
    logger = EOLogging().get_logger("eopf.daskconfig.dask_utils.wait_and_get")
    has_failure = False

    # Process real Dask Futures as they complete
    timeout = kwargs.pop("timeout", EOConfiguration()["dask_utils__timeout"])

    for future in as_completed(real_futures.values(), timeout=timeout):
        try:
            index = next(i for i, f in real_futures.items() if f == future)  # Find correct index
            try:
                results[index] = future.result()
                del real_futures[index]
            except CancelledError as e:
                logger.warning(f"Task {future} has been cancelled : {e}")
                has_failure = True
            except TimeoutError as e:
                logger.warning(f"Task {future} is in timeout : {e}")
                has_failure = True
            except Exception as e:
                logger.warning(f"Task {future} is in error : {e}")
                if cancel_at_first_error:
                    client.cancel(real_futures)
                has_failure = True
        except StopIteration as e:
            raise DaskComputingError(f"Can't find {future} in the list of real_futures") from e
    gc.collect()
    if has_failure:
        raise DaskComputingError(f"Error occurred during dask computation on {real_futures}")


def cancel_futures(
    futures: list[FutureLike | Future],
    **kwargs: Any,
) -> None:
    """
    Function to cancel the futures list and return the results.
    Order is kept.
    FutureLike objects are accepted

    """

    indexed_futures = dict(enumerate(futures))  # Store index-future mapping
    real_futures = {i: f for i, f in indexed_futures.items() if isinstance(f, Future)}

    # Process real Dask Futures as they complete
    if len(real_futures) != 0:
        client = get_distributed_client()
        if client is not None:
            client.cancel(real_futures, force=kwargs.get("force", False))
        else:
            raise DaskComputingError("Dask future cancellation requested but no Client available !!!!")

        gc.collect()


def scatter(data: Array, **kwargs: Any) -> Future | Array:
    """
    Generalized scatter function
    works also in case no distributed client is available

    Parameters
    ----------
    data
    kwargs

    Returns
    -------

    """
    logger = EOLogging().get_logger("eopf.dask_utils.dask_utils")
    client = get_distributed_client()

    if client is not None:
        logger.debug(f"scattering on client client {id(client)} with options : {kwargs}")
        timeout = kwargs.pop("timeout", EOConfiguration()["dask_utils__timeout"])
        return client.scatter(data, timeout=timeout, **kwargs)
    # No client, can't future the data
    logger.debug("No client in scatter : returning data itself ")
    return data


def get_distributed_client() -> Client | None:
    """
    Get the client, None if not available
    """
    try:
        client = get_client()
    except ValueError:
        client = None
    return client


def is_distributed() -> bool:
    """
    Get the distributed status
    Returns True only if a distributed client is available and un running status

    """
    logger = EOLogging().get_logger("eopf.dask_utils.dask_utils")
    client = get_distributed_client()

    if client is not None and client.status == "running":
        logger.debug(f"Distributed client detected : {id(client)}")
        return True

    # No client, can't future the data
    logger.debug("No distributed running client detected")
    return False


def is_worker_reachable(a_path: AnyPath) -> bool:
    """
    Test if an AnyPath is reachable from the workers
    This is primarily to test if it is a shared folder or an S3 folder

    warning ; Do this test after creating the daskcontext/client or it will only test local access to the path

    Parameters
    ----------
    a_path: AnyPath
        AnyPath to test access to

    Returns
    ----------
    bool : reachable or not


    """
    logger = EOLogging().get_logger("eopf.dask_utils.dask_utils")
    if is_distributed():
        client = get_distributed_client()
        if client is not None:
            global_result = True
            results = client.run(a_path.exists)
            for worker, is_reachable in results.items():
                if is_reachable:
                    logger.debug(f"Path {a_path} reachable for {worker}")
                else:
                    global_result = False
                    logger.debug(f"Path {a_path} NOT reachable for {worker}")
            return global_result
        return a_path.exists()
    return a_path.exists()


def wait_for_workers(minimum_workers: int = 1, timeout: int = 60) -> None:
    """

    Parameters
    ----------
    minimum_workers : minimum number of worker to wait for
    timeout : timeout to wait for these workers to be available

    Returns
    -------
    None

    Raises
    ------
    DaskClusterTimeout :  when timeout is reached


    """
    if minimum_workers == 0:
        return
    if is_distributed() and (client := get_distributed_client()) is not None:
        start = time.time()
        while True:
            n_workers = len(client.scheduler_info().get("workers", {}))
            if n_workers >= minimum_workers:
                return
            if time.time() - start > timeout:
                raise DaskClusterTimeout(f"Cluster {client.cluster}, Timed out waiting for {minimum_workers} workers.")
            time.sleep(5)
