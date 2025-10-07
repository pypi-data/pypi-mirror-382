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
"""the eopf.logging module provide a simple and homogeneous interface to the logging system.
As logging system we chose that defined by the Python standard, for compatibility and spread of usage reasons.
Since, a developer might need to use various logging configurations,
we provide a factory of loggers, i.e. EOLogFactory.
The factory is able to create loggers based on given logging configurations.
A configuration can be specified through JSON files, since JSON format is commonly used in eopf-cpm.

By default EOLogFactory uses the “default.json” file for logging configuration, located in eopf.logging.conf folder.
All logging configurations placed in the previous mentioned folder are automatically loaded by the factory.
Nevertheless, the developer can add configuration files from other locations,
either one by one or as a register_requested_parameter from a given folder.

For uniformity reasons we require the developers to use only
the message formatters specified in the default configurations.
That is console message format for displaying message to the standard
output or file message format for log messages written to any other output (mainly files)

Moreover, we provide a dask logging configuration file in the eopf.logging.conf folder, I.e.dask.yaml.,
which we can be used to configure dask logging. Thus, providing a uniform logging system for all eopf-cpm usage.
"""

from .log import EOLogging

__all__ = [
    "EOLogging",
]
