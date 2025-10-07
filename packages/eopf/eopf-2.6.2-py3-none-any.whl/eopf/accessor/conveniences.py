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

conveniences.py

Convenience utility function

"""

import contextlib
from typing import Any, Iterator

from eopf.accessor import EOAccessor
from eopf.common.constants import OpeningMode
from eopf.logging import EOLogging


@contextlib.contextmanager
def open_accessor(
    accessor: EOAccessor,
    mode: OpeningMode | str = OpeningMode.OPEN,
    **kwargs: Any,
) -> Iterator[EOAccessor]:
    """Open an EOAccessor in the given mode.

    help you to open EOAccessor
    it as a standard python open function.

    Parameters
    ----------
    accessor: EOAccessor
        accessor to open
    mode: OpeningMode | str , optional
       mode to open the store; default to open
    kwargs: any
        store specific kwargs

    Returns
    -------
    store
        store opened with given arguments

    See Also
    --------
    EOProductStore.open
    """
    logger = EOLogging().get_logger("eopf.accessor.conveniences")
    try:
        logger.debug(f"Opening : {accessor}")
        accessor.open(mode=mode, **kwargs)
        yield accessor
    finally:
        accessor.close()
