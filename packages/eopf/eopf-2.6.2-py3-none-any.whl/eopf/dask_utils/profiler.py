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
profiler.py

profiling tools

"""
from contextlib import ContextDecorator
from cProfile import Profile
from functools import wraps
from pathlib import Path
from pstats import Stats
from typing import Any, Optional, Self, Union

import dask

import eopf.dask_utils.dask_helpers
from eopf.exceptions import SingleThreadProfilerError


class single_thread_profiler(ContextDecorator):
    """Decorator/context manager function used to perform single threaded profiling (cProfile) on code running in dask

    Parameters
    ----------
    sort_by : pstat sort by when printed
    limit : number of element to display when printed
    report_name: str | None
        name of cProfile.Stats dump file, if None will print the result using sort_by and limit

    Raises
    ----------
    SingleThreadProfilerError
        When the single_thread_profiler raises any error

    Returns
    ----------
    The result of the computation

    Examples
    --------
    >>> @single_thread_profiler("stats.dump")
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    >>> @single_thread_profiler(limit=10, sort_by="tottime")
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    >>> with single_thread_profiler(limit=10, sort_by="tottime"):
    >>>     safe_store = EOSafeStore("data/olci.SEN3")
    >>>     nc_store = EONetCDFStore("data/olci.nc")
    >>>     convert(safe_store, nc_store)

    Notes
    -----
    In IPython environments one can use snakeviz to obtain a graphical representation of the returned Stats:
    >>> pip install snakeviz
    >>> %load_ext snakeviz
    >>> %snakeviz stats.dump

    See Also
    -------
    pstats.Stats
    """

    def __init__(self, report_name: Optional[Union[Path, str]] = None, limit: int = 20, sort_by: str = "cumtime"):
        self.report_name = report_name
        self.limit = limit
        self.sort_by = sort_by
        self.profiler = Profile()
        self.dask_context: Optional[dask.config.set] = None

    def __enter__(self) -> Self:
        # Check for distributed client

        if eopf.dask_utils.dask_helpers.get_distributed_client() is not None:
            raise SingleThreadProfilerError(
                "A Dask distributed client is active. cProfile can't capture "
                "worker activity, use distributed_profiler on dask context",
            )

        # Activate single-threaded scheduler
        self.dask_context = dask.config.set(scheduler="single-threaded")
        self.dask_context.__enter__()

        self.profiler.enable()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.profiler.disable()
        if self.dask_context is not None:
            self.dask_context.__exit__(exc_type, exc_value, traceback)

        if self.report_name:
            self.profiler.dump_stats(self.report_name)
        else:
            stats = Stats(self.profiler).sort_stats(self.sort_by)
            stats.print_stats(self.limit)

    def __call__(self, func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with self:
                return func(*args, **kwargs)

        return wrapper
