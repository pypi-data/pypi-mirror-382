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
from os import linesep
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, Hashable, Iterable, List, Optional, Tuple, Union

from eopf.common.constants import DIMENSIONS_NAME, Style
from eopf.config.config import EOConfiguration
from eopf.exceptions import EOObjectMultipleParentError, InvalidProductError
from eopf.product.eo_abstract import EOAbstract

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_product import EOProduct


class EOObject(EOAbstract, ABC):
    """Abstract class implemented by EOGroup and EOVariable.
    Provide local attribute.
    Implement product affiliation and path access.
    Doesn't implement the attrs.

    Parameters
    ----------
    name: str, optional
        name of this group
    parent: EOProduct or EOGroup, optional
        parent
    dims: tuple[str], optional
        dimensions to assign
    """

    def __init__(
        self,
        name: str,
        parent: Optional["EOObject"] = None,
        **kwargs: Any,
    ) -> None:
        self._name: str = name
        self._parent: Optional[EOObject] = parent
        self._repath(name, parent)
        self._kwargs = kwargs

        if "mask_and_scale" not in kwargs:
            self._kwargs["mask_and_scale"] = EOConfiguration().get("product__mask_and_scale")

    def __reduce__(self) -> Union[str, Tuple[Any, ...]]:
        raise TypeError("Class is not serializable !!! ")

    def __eq__(self, other: Any) -> bool:
        """
        test the equal ==
        Parameters
        ----------
        other

        Returns
        -------

        """
        if not isinstance(other, EOObject):
            raise NotImplementedError
        return self.name == other.name

    def _repath(self, name: str, parent: Optional["EOObject"]) -> None:
        """Set the name, product and relative_path attributes of this EObject.
        This method does not modify the path of the object, even if this is the child of a multiple product.

        Parameters
        ----------
        name: str
            name of this object
        parent: EOProduct or EOGroup, optional
            parent to link to this group

        Raises
         ------
         EOObjectMultipleParentError
             If the object has a product and a not undefined attribute is modified.

        """
        if self._parent is not None:
            if self._name not in ("", name):
                raise EOObjectMultipleParentError("The EOObject name does not match it's new path")
            if self._parent is not parent:
                raise EOObjectMultipleParentError("The EOObject product does not match it's new parent")

        self._name = name
        self._parent = parent

    # docstr-coverage: inherited
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, aname: str) -> None:
        self._name = aname

    @property
    def kwargs(self) -> dict[str, Any]:
        return self._kwargs

    @property
    def is_root(self) -> "bool":
        """
        Default to not being the root
        """
        return False

    @property
    def parent(self) -> Optional["EOObject"]:
        """
        Parent Container/Product of this object in it's Product.

        Returns
        -------

        """
        return self._parent

    @parent.setter
    def parent(self, parent: "EOObject") -> None:
        """Set parent of current EOObject"""
        self._parent = parent

    # docstr-coverage: inherited
    @property
    def path(self) -> str:
        if self.parent is None:
            return self.name
        return str(PurePosixPath(self.parent.path) / self.name)

    # docstr-coverage: inherited
    @property
    def product(self) -> "EOProduct":
        """
        go down to the trunk of the tree to get the product
        """
        if self.parent is None:
            raise InvalidProductError("Undefined parent")
        return self.parent.product

    # docstr-coverage: inherited
    @property
    def relative_path(self) -> Iterable[str]:
        rel_path: list[str] = []
        if self.parent is not None:
            if self.parent.is_root:
                return ["/"]
            rel_path.extend(self.parent.relative_path)
            rel_path.append(self.parent.name)
        return rel_path

    @property
    @abstractmethod
    def attrs(self) -> dict[str, Any]:
        """

        Returns
        -------
        Attributes dict
        """

    @attrs.setter
    @abstractmethod
    def attrs(self, new_attrs: dict[str, Any]) -> None:
        """

        Returns
        -------
        Attributes dict
        """

    def eopf_type(self) -> str:
        """
        Get the eopf type is available else raise exception
        Returns
        -------


        """
        return self.attrs["stac_discovery"]["eopf:type"]

    def tree(self, return_tree: bool = False, detailed: bool = False) -> Optional[str]:
        """Display or return the hierarchy of the EOObject.

        Parameters
        ----------
        return_tree: bool
            return hierarchy as string representation and not print it

        Returns
        -------
        The tree in str
        """

        # Iterate and print EOObject structure
        buffer: List[str] = []
        self._print_tree_structure(buffer, self, continues=tuple(), level=0, detailed=detailed)

        indent = ""
        tree_str_repr = f"{indent}{linesep}".join(buffer)
        if return_tree:
            return tree_str_repr
        print(tree_str_repr)
        return None

    def __repr__(self) -> str:
        # Iterate and print EOProduct structure otherwise (CLI)
        buffer: List[str] = []
        self._print_tree_structure(buffer, self, continues=tuple(), level=0, detailed=True)
        # To print or not to print ?
        return "\n".join(buffer)

    def __str__(self) -> str:
        # Iterate and print EOProduct structure otherwise (CLI)
        buffer: List[str] = []
        self._print_tree_structure(buffer, self, continues=tuple(), level=0, detailed=False)
        # To print or not to print ?
        return "\n".join(buffer)

    @abstractmethod
    def _print_tree_structure(
        self,
        buffer: List[str],
        obj: Union["EOObject", tuple[str, "EOObject"]],
        continues: tuple[bool, ...],
        level: int,
        detailed: bool,
    ) -> None:
        """

        Parameters
        ----------
        obj
        level
        detailed

        Returns
        -------

        """

    @staticmethod
    def _compute_tree_indents(continues: tuple[bool, ...]) -> tuple[str, str]:
        style = Style()
        if not continues:
            pre = ""
            fill = ""
        else:
            items = [style.vertical if cont else style.empty for cont in continues]
            indent = "".join(items[:-1])
            branch = style.cont if continues[-1] else style.end
            pre = indent + branch
            fill = "".join(items)
        return fill, pre

    @abstractmethod
    def _repr_html_(self) -> str:  # pragma: no cover
        """

        Parameters
        ----------
        prettier

        Returns
        -------

        """


class EOObjectWithDims(EOObject, ABC):
    """Abstract class implemented by EOGroup and EOVariable.
    Provide local attribute and dimensions setter/accessor.
    Implement product affiliation and path access.
    Doesn't implement the attrs.

    Parameters
    ----------
    name: str, optional
        name of this group
    parent: EOProduct or EOGroup, optional
        parent
    dims: tuple[str], optional
        dimensions to assign
    """

    def __init__(
        self,
        name: str,
        parent: Optional[EOObject] = None,
        *,
        dims: tuple[str, ...] = tuple(),
        **kwargs: Any,
    ) -> None:
        super().__init__(name, parent, **kwargs)
        self.assign_dims(dims=dims)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EOObjectWithDims):
            raise NotImplementedError
        if not super().__eq__(other):
            return False
        return self.dims == other.dims

    @abstractmethod
    def assign_dims(self, dims: tuple[Hashable, ...]) -> None:
        """Assign dimension to this object

        Parameters
        ----------
        dims: Iterable[str], optional
            dimensions to assign
        """

    @property
    def dims(self) -> tuple[str, ...]:
        """tuple[str, ...]: dimensions"""
        return tuple(self.attrs.get(DIMENSIONS_NAME, tuple()))
