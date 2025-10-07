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
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterable, MutableMapping, TypeVar

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_product import EOProduct

T = TypeVar("T", bound="EOAbstract")


class EOAbstract(ABC):  # pragma: no cover
    """Interface implemented by all EO class (EOProduct, EOGroup, EOVariable) and
    their parents (EOGroup, EOObject).

    Notes
    -----
        EOVariableOperatorsMixin doesn't inherit this class, being only a mixin class for EOVariable.
    """

    @property
    @abstractmethod
    def attrs(self) -> MutableMapping[str, Any]:
        """dict[str, Any]: Dictionary of this EOObject attributes."""

    @property
    @abstractmethod
    def name(self) -> str:
        """str: Name of this object. Empty string if unnamed."""

    @property
    @abstractmethod
    def path(self) -> str:
        """str: Path from the top level EOProduct to this object.
        It's a string following Linux path conventions."""

    @property
    @abstractmethod
    def product(self) -> "EOProduct":
        """EOProduct: Product related to this object.

        Raises
        ------
        InvalidProductError
            If this object doesn't have a (valid) product.
        """

    @property
    @abstractmethod
    def is_root(self) -> "bool":
        """
        Define if the element is a root of the data tree
        """

    @property
    @abstractmethod
    def relative_path(self) -> Iterable[str]:
        """Iterable[str]: Relative path of this object.
        It's the register_requested_parameter of the names of this object parents (Product name as '/')."""
