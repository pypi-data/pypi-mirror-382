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
geometry_utils.py

geometry utils for bounding box, footprint ...

"""
from typing import Any

import numpy as np


def bbox_block(
    x_block: np.ndarray[Any, np.dtype[Any]],
    y_block: np.ndarray[Any, np.dtype[Any]],
    block_id: tuple[int, int],
    chunksize: tuple[int, int],
    region: tuple[int, int, int, int],
    is_geographic: bool,
    max_index: int = 99999999,
    min_index: int = -1,
) -> np.ndarray[Any, np.dtype[Any]]:
    """
    Determines min and max of pixel coordinates in a block for the geo-region.

    Parameters
    ----------
    x_block:
        x coordinates 2-D ndarray
    y_block:
        y coordinates 2-D ndarray
    block_id:
        (block_row, block_col) block position, to calculate the pixel offset
    chunksize:
        (chunksize_y, chunksize_x) block nominal size, to calculate the pixel offset
    region:
        geo box as tuple lon,lat,width,height
    is_geographic:
        whether x and y are lon and lat

    Returns
    -------
    3-D array of shape (4,1,1) with min_x, min_y, max_x, max_y, to be put in a mosaic by map_blocks
    """
    x_pos = np.tile(
        np.arange(x_block.data.shape[1]) + block_id[-1] * chunksize[1],  # type: ignore
        (x_block.shape[0], 1),
    )
    y_pos = np.tile(
        (np.arange(y_block.data.shape[0]) + block_id[-2] * chunksize[0]).reshape(  # type: ignore
            (x_block.shape[0], 1),
        ),
        (1, x_block.shape[1]),
    )
    if is_geographic:
        inside = (
            ((x_block - region[0]) % 360.0 <= 180.0)
            & ((x_block - (region[0] + region[2])) % 360.0 > 180.0)
            & (y_block >= region[1])
            & (y_block < region[1] + region[3])
        )
    else:
        inside = (
            (x_block >= region[0])
            & (x_block < region[0] + region[2])
            & (y_block >= region[1])
            & (y_block < region[1] + region[3])
        )
    if np.any(inside):
        i_min = np.min(x_pos[inside])
        i_max = np.max(x_pos[inside])
        j_min = np.min(y_pos[inside])
        j_max = np.max(y_pos[inside])
    else:
        i_min = j_min = max_index
        i_max = j_max = min_index
    return np.array([i_min, j_min, i_max, j_max]).reshape((4, 1, 1))
