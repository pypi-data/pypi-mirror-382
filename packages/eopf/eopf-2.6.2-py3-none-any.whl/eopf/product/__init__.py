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
"""eopf.product module provide to the developers of the re-engineered processors
a homogeneous access interface to Copernicus products.

This module allows loading, updating and storing in parallel Copernicus products from/to multiple storage systems
(S3, NFS, POSIX …) and using different formats (Zarr, NetCDF4(HDF5), Cloud optimised GeoTIFF).

The eopf.product module also provides an opportunistic caching mechanism
used to store intermediary results into L0 products.
This cache is used to store computing results so that they can be reused
if a product is reprocessed. The most interesting calculation results to cache are those
that have a low probability of change in case of reprocessing, are time consuming to produce and are small in size.

The eopf.product module is composed mainly by the following two sub-packages:

    * eopf.product.core
    * eopf.product.store
"""

from eopf.product.eo_container import EOContainer
from eopf.product.eo_group import EOGroup
from eopf.product.eo_product import EOProduct
from eopf.product.eo_variable import EOVariable

__all__ = ["EOGroup", "EOProduct", "EOVariable", "EOContainer"]
