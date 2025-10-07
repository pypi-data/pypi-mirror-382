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
"""The eopf.triggering module simplifies the integration of processing units
with the most widespread processing orchestration systems
(Spring Cloud Data Flow, Apache Airflow, Zeebee, Apache Beam ...).
"""

from eopf.triggering.runner import EORunner

__all__ = ["EORunner"]
