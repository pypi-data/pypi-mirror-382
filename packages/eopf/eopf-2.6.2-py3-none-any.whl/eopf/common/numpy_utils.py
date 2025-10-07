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
numpy_utils.py

numpy utilities

"""
from typing import Any

import numpy as np
from s3fs import S3File


def froms3file(fsfile: S3File, dtype: Any = np.float32, count: int = -1, offset: int = 0) -> Any:
    """
    NumPy-compatible np.fromfile replacement for s3fs.S3File objects.

    Parameters
    ----------
    fsfile : s3fs.S3File
        Opened file-like object from s3fs (opened in 'rb' mode).
    dtype : data-type, optional
        Data type of the returned array. Default: float.
    count : int, optional
        Number of items to read. Default -1 means read all data.
    offset : int, optional
        Byte offset in the file before reading.
    """
    dtype = np.dtype(dtype)

    # Seek to offset (in bytes)
    fsfile.seek(offset, 0)

    # Determine how many bytes to read
    if count == -1:
        nbytes = -1
    else:
        nbytes = count * dtype.itemsize

    # Read raw bytes
    data = fsfile.read(nbytes)

    # Convert to NumPy array
    return np.frombuffer(data, dtype=dtype, count=count)
