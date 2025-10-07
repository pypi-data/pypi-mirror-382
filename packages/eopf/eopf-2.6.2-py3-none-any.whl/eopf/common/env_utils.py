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

env_utils.py

env utils to set/get env variables etc


"""


import contextlib
import os
from typing import Any, ContextManager, Iterator


@contextlib.contextmanager
def env_context(environ: dict[str, str]) -> Iterator[os._Environ[str]]:
    """Context that temporarily register the process environment variables."""
    old_environment = os.environ.copy()
    os.environ.update(environ)
    try:
        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(old_environment)


def env_context_eopf() -> ContextManager[os._Environ[str]]:
    import eopf  # pylint: disable=import-outside-toplevel

    eopf_path = os.path.dirname(eopf.__file__)
    return env_context({"EOPF_ROOT": eopf_path})


def resolve_env_vars(data: Any) -> Any:
    """
    Recursively resolve env var in dict/str etc
    """
    if isinstance(data, dict):
        resolved_data = {}
        for key, value in data.items():
            resolved_key = resolve_env_vars(key)
            resolved_value = resolve_env_vars(value)
            resolved_data[resolved_key] = resolved_value
        return resolved_data
    if isinstance(data, list):
        return [resolve_env_vars(it) for it in data]
    if isinstance(data, str):
        return os.path.expandvars(data)
    return data
