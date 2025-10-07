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
type_utils.py

utilities to handle type issues

Numpy etc

"""
import datetime
from typing import Any, Callable, Literal, Mapping, Optional, Sequence, Union

import numpy as np

from eopf.common import date_utils


def convert_to_native_python_type(obj: Any) -> Any:
    """
    Convert an object to native python data types if possible,
    otherwise return the obj as it is

    Parameters
    ----------
    obj: Any
        an object

    Returns
    ----------
    Any
        either the obj converted to native Python data type,
        or the obj as received
    """
    conversion_map: dict[Any, Callable[[Any], Any]] = {
        dict: convert_dict_to_native_python_type,
        list: convert_iterable_to_native_python,
        tuple: convert_iterable_to_native_python,
        set: convert_iterable_to_native_python,
        np.ndarray: convert_numpy_array_to_native_python_type,
        np.bool_: bool,
        str: str,
        datetime.datetime: date_utils.convert_to_unix_time,
        float: float,
    }
    # check dict
    for t, f in conversion_map.items():
        if isinstance(obj, t):
            return f(obj)

    # check np int
    if isinstance(obj, (*get_managed_numpy_dtype("int"), int)) and not isinstance(obj, bool):
        return int(obj)

    # check np float
    if isinstance(obj, (*get_managed_numpy_dtype("float"), float)):
        return float(obj)

    if isinstance(obj, bytes):
        return obj.decode()

    # if no conversion can be done
    return obj


def convert_numpy_array_to_native_python_type(obj: Any) -> Any:
    return [convert_to_native_python_type(i) for i in obj.tolist()]


def convert_iterable_to_native_python(obj: Any) -> Any:
    return type(obj)(map(convert_to_native_python_type, obj))


def convert_dict_to_native_python_type(obj: Any) -> Any:
    res = {}
    for k, v in obj.items():
        res[k] = convert_to_native_python_type(v)
    return res


def reverse_conv(data_type: Any, obj: Any) -> Any:
    """Converts the obj to the data_type

    Parameters
    ----------
    data_type: Any
        the data type to be converted to
    obj: Any
        an object

    Returns
    ----------
    Any
    """
    for dtype in get_managed_numpy_dtype():
        if np.dtype(data_type) == np.dtype(dtype):
            return dtype(obj)
    return obj


def get_managed_numpy_dtype(type_: Optional[str] = None) -> tuple[type, ...]:
    """Retrieve OS dependent dtype for numpy"""
    managed_type: dict[str, Sequence[str]] = {"uint": ("uint64", "uint32", "uint16", "uint8")}
    managed_type["int"] = ("int64", "int32", "int16", "int8", *managed_type["uint"])
    managed_type["float"] = ("float64", "float32", "float16")
    if type_:
        types = managed_type.get(type_, tuple())
    else:
        types = [dtype for type_group in managed_type.values() for dtype in type_group]
    return tuple(getattr(np, attr) for attr in types if hasattr(np, attr))


Chunk = Union[
    None,
    int,
    Literal["auto"],
    tuple[int, ...],
    Mapping[Any, int | Literal["auto"] | tuple[int, ...] | None],
]


class Singleton(type):
    """
    Singleton pattern holder to use as metaclass

    Can hold multiple singleton in the same

    """

    _instances: dict[Any, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clear(cls) -> None:
        cls._instances.pop(cls, None)


def format_bytes(nbytes: int) -> str:
    """Human-readable bytes formatter"""
    if nbytes < 1024:
        return f"{nbytes} B"
    if nbytes < 1024**2:
        return f"{nbytes/1024:.1f} KB"
    if nbytes < 1024**3:
        return f"{nbytes/1024**2:.1f} MB"
    return f"{nbytes/1024**3:.1f} GB"
