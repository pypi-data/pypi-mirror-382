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
eo_container.py

EOContainer implementation

"""
import copy
import warnings
from pathlib import PurePosixPath
from typing import (
    TYPE_CHECKING,
    Any,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    MutableMapping,
    Optional,
    Self,
    Union,
    ValuesView,
    cast,
)

from deepdiff import DeepDiff

from eopf.common.constants import (
    DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
    EOCONTAINER_CATEGORY,
    EOPF_CATEGORY_ATTR,
    EOPF_CPM_PATH,
)
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import is_last
from eopf.exceptions import EOContainerSetitemError, InvalidProductError
from eopf.product.conveniences import get_default_file_name_no_extension
from eopf.product.eo_group import EOGroup
from eopf.product.eo_object import EOObject
from eopf.product.eo_product import EOProduct
from eopf.product.eo_variable import EOVariable
from eopf.product.rendering import renderer

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_validation import ValidationMode


class EOContainer(EOObject):
    """
    specialized dict to retain products and do additional things such as stac attributes etc

    """

    @staticmethod
    def create_from_products(
        name: str,
        products: Iterable["EOProduct" | Self],
        container_type: Optional[str] = None,
    ) -> "EOContainer":
        """
        Create EOContainer from iterable of EOContainers/EOProducts

        Parameters
        ----------
        name: str
            name of EOContainer
        products: Iterable["EOProduct" | Self]
            iterable of products
        container_type: Optional str
            container type

        Raises
        -------
        EOContainerSetitemError

        Returns
        -------
        EOContainer
        """
        for product in products:
            if len(product.name) == 0:
                raise EOContainerSetitemError("Product names must be defined properly")

        # create container
        container = EOContainer(name, type=container_type)

        # iterate over products and add them to the container
        for product in products:
            container[product.name] = product

        return container

    def __init__(
        self,
        name: str,
        attrs: Optional[MutableMapping[str, Any]] = None,
        type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, **kwargs)
        self._prod_dict: dict[str, EOProduct | EOContainer] = {}
        self._attrs: dict[str, Any] = dict(attrs) if attrs is not None else {}
        self._mission_specific: Optional[str] = None

        if type is None:
            if attrs is None:
                product_type: Optional[str] = None
            else:
                try:
                    product_type = attrs["stac_discovery"]["properties"]["product:type"]
                except KeyError:
                    product_type = None
        else:
            product_type = type

        self.container_type: Optional[str] = product_type

        self._declare_as_container()

    @property
    def attrs(self) -> dict[str, Any]:

        for prod in self.keys():
            self._add_product_to_assets(prod)
        return self._attrs

    @attrs.setter
    def attrs(self, new_attrs: dict[str, Any]) -> None:
        self._attrs = new_attrs

    @property
    def mission_specific(self) -> Optional[str]:
        return self._mission_specific

    @mission_specific.setter
    def mission_specific(self, amission_specific: str) -> None:
        self._mission_specific = amission_specific

    @property
    def type(self) -> Optional[str]:
        """

        Returns
        -------

        """
        warnings.warn("Use container_type instead", DeprecationWarning)
        return self.container_type

    @property
    def container_type(self) -> Optional[str]:
        """
        Retrieve product_type, None if not set

        Returns
        -------
        from attribute ["stac_discovery"]["properties"]["product:type"]
        """
        try:
            return self.attrs["stac_discovery"]["properties"]["product:type"]
        except KeyError:
            try:
                # support old EOPF products
                return self.attrs["stac_discovery"]["properties"]["eopf:type"]
            except KeyError:
                return None

    @container_type.setter
    def container_type(self, intype: Optional[str]) -> None:
        """
        Set product_type

        Parameters
        ----------
        inversion: str
        """
        if intype is not None:
            self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["product:type"] = intype

    @property
    def processing_version(self) -> Optional[str]:
        """
        Retrieve processing_version

        Returns
        -------
        from attribute ["stac_discovery"]["properties"]["processing:version"]
        """
        try:
            return self.attrs["stac_discovery"]["properties"]["processing:version"]
        except KeyError:
            return None

    @processing_version.setter
    def processing_version(self, inversion: str) -> None:
        """
        Set processing_version

        Parameters
        ----------
        inversion: str
        """
        self.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["processing:version"] = inversion

    @property
    def datasize(self) -> int:
        """
        Compute container datasize recursively

        Returns
        -------
        the datasize in bytes
        """
        total_size = 0
        for _, v in self.items():
            if isinstance(v, EOProduct):
                total_size += v.datasize
        return total_size

    def is_valid(self, validation_mode: Optional["ValidationMode"] = None) -> bool:
        """Check if the product is a valid eopf container

        Returns
        -------
        bool

        See Also
        --------
        EOProduct.validate
        """
        # Mandtory lazy import for circular deps
        from eopf.product import (
            eo_container_validation,  # pylint: disable=import-outside-toplevel
        )

        flag, _ = eo_container_validation.is_valid_container(self, validation_mode=validation_mode)
        return flag

    def validate(self, validation_mode: Optional["ValidationMode"] = None) -> None:
        """check if the product is a valid eopf container, raise an error if is not a valid one

        Raises
        ------
        InvalidProductError
            If the product not follow the harmonized common data model

        See Also
        --------
        EOProduct.is_valid
        """
        if not self.is_valid(validation_mode=validation_mode):
            raise InvalidProductError(f"Invalid container {self} with mode {str(validation_mode)}")

    def __setitem__(self, key: str, value: Union["EOProduct", "EOContainer", "EOGroup", "EOVariable"]) -> None:
        """
        Add "EOProduct", "EOContainer", "EOGroup", "EOVariable" to an EOContainer

        Parameters
        ----------
        key: str
            path of the value inside the container
        value: Union["EOProduct", "EOContainer", "EOGroup", "EOVariable"]
            object to be added

        Raises
        -------
        EOContainerSetitemError
        """

        if len(key) == 0:
            raise KeyError("Empty key is not accepted in eocontainer")

        if key == "/":
            raise KeyError("Key can not be root")

        if key.startswith("/"):
            key = key[1:]

        eopath = PurePosixPath(key)

        if eopath.is_absolute():
            # do not consider root "/" as a part
            # as it refers to self/current container
            eopath_parts = eopath.parts[1:]
        else:
            eopath_parts = eopath.parts

        if isinstance(value, (EOContainer, EOProduct)):
            if len(eopath_parts) > 1:
                # recursively add the EOProduct/EOContainer
                sub_key = "/".join(eopath_parts[1:])
                sub_obj = self[eopath_parts[0]]
                sub_obj[sub_key] = value
                value.parent = self
            else:
                # add product/container to current object
                self._prod_dict[key] = value
                value.parent = self
                self._add_product_to_assets(key)

        else:
            # isinstance(value, (EOVariable, EOGroup)):
            # EOVariables can not be attached to EOContainers
            # hence, we need to discover a descendant EOProduct and attach the EOV to it
            i = 0
            sub_obj = self
            while not isinstance(sub_obj, EOProduct) and i < len(eopath_parts):
                # recursively search for an EOProduct
                sub_obj = sub_obj[eopath_parts[i]]
                i += 1

            if i == len(eopath_parts):
                # when there is no EOProduct we can not attach the EOV
                raise EOContainerSetitemError(
                    "EOVariables and EOGroups can only be added to an EOProduct,"
                    "which does not exist in the given path hierarchy {key}",
                )

            # attach the EOV to the EOP
            eoproduct_path = "/".join(eopath_parts[i:])
            sub_obj[eoproduct_path] = value

    def __getitem__(self, item: str) -> Union["EOProduct", "EOContainer"]:
        return self._prod_dict[item]

    def __delitem__(self, key: str) -> None:
        self._remove_product_from_assets(key)
        del self._prod_dict[key]

    def __iter__(self) -> Iterator["str"]:
        yield from iter(self._prod_dict)

    def __len__(self) -> int:
        return len(self._prod_dict)

    def __eq__(self, other: Any) -> bool:
        # Check if the other object is an instance of EOContainer
        if not isinstance(other, EOContainer):
            return False

        # Check if the two EOContainer have the same structure
        if sorted(list(self.keys())) != sorted(list(other.keys())):
            return False

        # Compare the two EOContainer attributes
        if DeepDiff(
            self.attrs,
            other.attrs,
            ignore_order=True,
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
        ):  # True when DeepDiff returns not empty dict
            return False

        # Compare each contained EOContainer or EOProduct
        for item_key in self:
            if self[item_key] != other[item_key]:  # compare sub-containers or eoproducts
                return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __deepcopy__(self, memo: dict[int, Any]) -> "EOContainer":
        new_instance: EOContainer = EOContainer(
            self.name,
            copy.deepcopy(self.attrs),
            self.container_type if self.container_type is not None else "",
        )
        for k, v in self._prod_dict.items():
            new_instance[k] = copy.deepcopy(v)
        new_instance._mission_specific = copy.deepcopy(self._mission_specific)
        memo[id(self)] = new_instance
        return new_instance

    def _repr_html_(self, prettier: bool = True) -> str:
        """Returns the html representation of the current container displaying the tree.

        Parameters
        ----------
        prettier: str
            Flag for using SVG as label for each Product, Group, Variable, Attribute.
        """

        css_file = EOPF_CPM_PATH / "product/templates/static/css/style.css"

        with css_file.open(mode="r") as css:
            css_content = css.read()

        css_str = f"<style>{css_content}</style>\n"
        rendered_template = renderer("container.html", container=self, prettier=prettier)
        final_str = css_str + rendered_template

        return final_str

    def _print_tree_structure(
        self,
        buffer: List[str],
        obj: Union["EOObject", tuple[str, "EOObject"]],
        continues: tuple[bool, ...],
        level: int,
        detailed: bool,
    ) -> None:
        """
        print tree structure of the container in he buffer

        Parameters
        ----------
        buffer
        obj
        continues
        level
        detailed

        Returns
        -------

        """
        if isinstance(obj, tuple):
            cont = obj[1]
        else:
            cont = obj
        if not isinstance(cont, EOContainer):
            return

        _, pre = EOObject._compute_tree_indents(continues)
        buffer.append(f"{pre}Container({cont.name})")
        level += 1
        for var, last in is_last(cont.values()):
            var._print_tree_structure(buffer, var, continues + (not last,), level, detailed)

    def items(self) -> ItemsView[str, "EOProduct" | Self]:
        return cast(ItemsView[str, EOProduct | Self], self._prod_dict.items())

    def keys(self) -> KeysView[str]:
        return self._prod_dict.keys()

    def values(self) -> ValuesView["EOProduct" | Self]:
        return cast(ValuesView[EOProduct | Self], self._prod_dict.values())

    def get_default_file_name_no_extension(self, mission_specific: Optional[str] = None) -> str:
        """
        See eopf.product.conveniences.get_default_file_name_no_extension
        """
        if mission_specific is None and self.mission_specific is not None:
            mission_specific = self.mission_specific
        if self.container_type is None:
            raise InvalidProductError("Container Type is mandatory to request the default filename")
        return get_default_file_name_no_extension(self.container_type, self.attrs, mission_specific=mission_specific)

    def export_dask_graph(self, folder: AnyPath) -> None:
        for v in self:
            self[v].export_dask_graph(folder)

    @property
    def is_root(self) -> "bool":
        """
        Container are considered root
        Returns
        -------

        """
        return self.parent is None

    def _declare_as_container(self) -> None:
        self._attrs.setdefault("stac_discovery", {}).setdefault("links", [])
        self._attrs.setdefault("other_metadata", {}).setdefault(EOPF_CATEGORY_ATTR, EOCONTAINER_CATEGORY)

    def _add_product_to_assets(self, prod_name: str) -> None:
        assets_dict = self._attrs.setdefault("stac_discovery", {}).setdefault("assets", {})
        assets_dict[prod_name] = {"href": prod_name}

    def _remove_product_from_assets(self, prod_name: str) -> None:
        self._attrs.setdefault("stac_discovery", {}).setdefault("assets", {}).pop(prod_name)

    @staticmethod
    def is_container(objwithattr: Any) -> "bool":
        """
        Test is the object has the elements to be considered a container
        Mostly tests on the STAC attribute links and category in other:metadata

        Parameters
        ----------
        objwithattr: any EO object or other that has attrs access

        Returns
        -------

        """
        if isinstance(objwithattr, EOContainer):
            return True
        try:
            return (
                "links" in objwithattr.attrs["stac_discovery"]
                and isinstance(objwithattr.attrs["stac_discovery"]["links"], list)
                and objwithattr.attrs["other_metadata"][EOPF_CATEGORY_ATTR] == EOCONTAINER_CATEGORY
            )
        except KeyError:
            return False
