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
progress.py

progress bar implementation including dask one

"""
from datetime import datetime
from typing import Any, Callable, Optional

from dask.diagnostics import ProgressBar
from dask.distributed import progress

from eopf.exceptions import ProgressConfigurationError, ProgressStepProgress
from eopf.exceptions.errors import TriggeringInternalError
from eopf.logging import EOLogging

CARRIAGE_RETURN = "\r"


class EOProgress:
    """A progress bar ,

    Parameters
    ----------
    url: str
        file path to the legacy format manifest xml

    Attributes
    ----------
    _max_progress: int
        the maximum dimension of the progress bar in characters
    _bar_width: int
        the dimension of the progress bar in characters
    _report_path: str
        path to a file where the time reports for each step will be written
    _cfg_set: bool : bool
        indicator if configuration has been established

    Examples
    --------
    >>> with EOProgress().cfg() as p:
    >>> for i in range(10):
    ...     time.sleep(0.5)
    ...     p.step(step_progress=10)
    ...

    >>> def a_func():
    ...     time.sleep(0.5)
    ...     EOProgress().step("first", step_progress=5)
    ...     time.sleep(1)
    ...     EOProgress().step("second", step_progress=10)
    ...     time.sleep(2)
    ...     EOProgress().step("third", step_progress=20)
    ...     time.sleep(4)
    ...     EOProgress().step("fourth", step_progress=40)
    ...     time.sleep(2.5)
    ...     EOProgress().step("fifth", step_progress=25)
    ...
    >>> with EOProgress().cfg() as p:
    ...     a_func()
    """

    def __init__(self) -> None:
        self._step_start_time: datetime = datetime.now()
        self._max_progress: int = 100
        self._bar_width: int = 100
        self._report_path: str = "./eopf/tracing/progress.log"
        self._cfg_set: bool = False
        self._progress: int = 0
        self._start_time = datetime.now()
        self._end_time = datetime.now()
        self.logger = EOLogging().get_logger("eopf.tracing")

    def __enter__(self) -> "EOProgress":
        """Function that ensure the setup of the EOProgress upon entering the with clause"""

        if not self._cfg_set:
            raise ProgressConfigurationError(
                "Do register_requested_parameter the configuration before using the EOProgress",
            )
        self._progress = 0
        self._draw_progress_bar()
        open(self._report_path, "w", encoding="utf-8").close()
        self._start_time = datetime.now()
        self._step_start_time = self._start_time
        return self

    def __exit__(self, *_: Any) -> None:
        """Function that ensures the reset of the EOProgress exiting the with clause"""

        self._end_time = datetime.now()
        elapsed_time = self._end_time - self._start_time
        if self._progress != self._max_progress:
            raise ProgressStepProgress(
                f"Update your step loads, the sum of the step_progress must be {self._max_progress}",
            )
        self.logger.info(f" Finished in {elapsed_time}")
        self._progress = 0
        self._max_progress = 1
        self._cfg_set = False

    def __new__(cls) -> "EOProgress":
        """Ensures there is only one object of EOProgress (singletone)"""

        if not hasattr(cls, "instance"):
            cls.instance = super(EOProgress, cls).__new__(cls)
        return cls.instance

    def cfg(
        self,
        max_progress: int = 100,
        bar_width: int = 100,
        report_path: str = "./eopf/tracing/progress.log",
    ) -> "EOProgress":
        """Function to register_requested_parameter the configuration attributes of the EOProgress

        Parameters
        ----------
        max_progress: int
            the maximum dimension of the progress bar in characters
        bar_width: int
            the dimension of the progress bar in characters
        report_path: str
            path to a file where the time reports for each step will be written

        Returns
        ----------
        EOProgress: returns the configured EOProgress
        """

        self._max_progress = max_progress
        self._bar_width = bar_width
        self._report_path = report_path
        self._cfg_set = True
        return self

    def step(self, msg: Optional[str] = None, step_progress: int = 1) -> None:
        """Function to mark the completion of one step

        Parameters
        ----------
        msg: str
            a message to be written in the report upon the completion of current step
        step_progress: int
            the amount of progress completed with this step
        """

        if self._progress < self._max_progress and (self._progress + step_progress) <= self._max_progress:
            step_end_time = datetime.now()
            elapsed_time_per_step = step_end_time - self._step_start_time
            self._progress += step_progress
            self._draw_progress_bar()
            progress_msg = f"Step {self._progress} finished in {elapsed_time_per_step}"
            if msg:
                progress_msg += f": {msg}"
            progress_msg += "\n"
            with open(self._report_path, mode="a", encoding="utf-8") as f:
                f.write(progress_msg)
            self._step_start_time = datetime.now()
        else:
            # TBD define propper error
            raise TriggeringInternalError("You have surpassed the total number of steps")

    def _draw_progress_bar(self) -> None:
        """Function to draw the progress bar"""

        if self._progress == 0:
            finished_bars = 0
        else:
            finished_bars = int((self._progress / self._max_progress) * self._bar_width)
        white_spaces = self._bar_width - finished_bars
        barr_str = CARRIAGE_RETURN + "[" + "#" * finished_bars + " " * white_spaces + "] " + str(self._progress) + "%"
        self.logger.info(barr_str)


def local_progress(fn: Callable[[Any, Any], Any]) -> Any:
    """Wrapper function used to output a progress bar for a local dask cluster

    Parameters
    ----------
    fn: Callable
        a function using dask computation

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    >>> @local_progress
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    ...
    """

    def wrap(*args: Any, **kwargs: Any) -> Any:
        pbar = ProgressBar()
        pbar.register()
        with ProgressBar():
            ret = fn(*args, **kwargs)
        pbar.unregister()

        return ret

    return wrap


def distributed_progress(fn: Callable[[Any, Any], Any]) -> Any:
    """Wrapper function used to output a progress bar for a distributed dask cluster

    Parameters
    ----------
    fn: Callable
        a function using dask computation

    Returns
    ----------
    Any: the return of the wrapped function

    Examples
    --------
    >>> @distributed_progress
    >>> def convert_to_native_python_type():
    ...     safe_store = EOSafeStore("data/olci.SEN3")
    ...     nc_store = EONetCDFStore("data/olci.nc")
    ...     convert(safe_store, nc_store)
    ...
    """

    def wrap(*args: Any, **kwargs: Any) -> Any:
        ret = fn(*args, **kwargs)
        progress(ret)

        return ret

    return wrap
