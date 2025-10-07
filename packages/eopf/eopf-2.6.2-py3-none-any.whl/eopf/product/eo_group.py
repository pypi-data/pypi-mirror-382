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
eo_group.py

EOGroup implementation

"""
import copy
import pprint
from collections.abc import MutableMapping
from typing import TYPE_CHECKING, Any, Hashable, Iterator, List, Optional, Union, cast

from deepdiff import DeepDiff
from xarray import Dataset

from eopf.common.constants import (
    DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
    DIMENSIONS_NAME,
    EOPF_CPM_PATH,
    Style,
)
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import is_last
from eopf.exceptions.errors import EOGroupInvalidRequestError
from eopf.logging import EOLogging
from eopf.product.eo_object import EOObject, EOObjectWithDims
from eopf.product.eo_variable import EOVariable
from eopf.product.rendering import renderer
from eopf.product.utils.eopath_utils import (
    downsplit_eo_path,
    is_absolute_eo_path,
    product_relative_path,
    remove_leading_char,
)

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_product import EOProduct


class EOGroup(EOObjectWithDims, MutableMapping[str, "EOObject"]):
    """Abstract class implemented by EOProduct and EOGroup.
    Storage of EOVariable and EOGroup, linked to their EOProduct's EOProductStore (if existing).
    Read and write both dynamically, or on demand to the EOProductStore.
    Can be used in a dictionary like manner with relatives and absolutes paths.

    Parameters
    ----------
    attrs: dict[str, Any], optional
        Attributes to assign
    """

    def __init__(
        self,
        name: str = "",
        parent: Optional["EOObject"] = None,
        *,
        variables: Optional[MutableMapping[str, "EOVariable"]] = None,
        attrs: Optional[MutableMapping[str, Any]] = None,
        dims: tuple[str, ...] = tuple(),
    ) -> None:
        self._logger = EOLogging().get_logger("eopf.product.eo_group")
        self._groups: dict[str, "EOGroup"] = {}
        self._attrs: dict[str, Any] = dict(attrs) if attrs is not None else {}
        # Add variables
        self._variables: dict[str, "EOVariable"] = {}
        variables = {} if variables is None else variables
        if not isinstance(variables, MutableMapping):
            raise TypeError("dataset parameters must be a MutableMapping")
        for key in variables:
            if not isinstance(key, str):
                raise TypeError(f"The dataset key {str(key)} is type {type(key)} instead of str")
        if parent is not None and not isinstance(parent, EOGroup):
            raise TypeError("Only EOGroup accepted as parent of group")
        # Need to init the EOObjectWithDims after attr sets
        EOObjectWithDims.__init__(self, name, parent, dims=dims)
        for var_name in variables:
            self[var_name] = variables[var_name]

    def __eq__(self, other: Any) -> bool:
        # Check if the other object is an instance of EOGroup
        if not isinstance(other, EOGroup):
            return False

        # Check if the two EOGroup have the same structure
        if sorted(list(self.keys())) != sorted(list(other.keys())):
            return False

        # Compare the two EOGroup attributes
        if DeepDiff(
            self.attrs,
            other.attrs,
            ignore_order=True,
            ignore_type_in_groups=DEEP_DIFF_IGNORE_TYPE_IN_GROUPS,
        ):  # True when DeepDiff returns not empty dict
            return False

        # Compare each contained EOGroup or EOVariable
        for item_key in self:
            if self[item_key].__ne__(other[item_key]):  # compare sub-groups or eovariables
                return False

        return True

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __copy__(self) -> "EOObject":
        cls = type(self)
        # cls_signature = inspect.signature(cls.__init__)
        # init_args = {k: getattr(self, k) for k in cls_signature.parameters if k != "self"}
        # return cls(**init_args)
        # self.load()
        new_instance = cls.__new__(cls)
        new_instance.__dict__.update(self.__dict__)
        return new_instance

    def __deepcopy__(self, memo: dict[int, Any]) -> "EOGroup":
        eo_vars = dict(self.variables)
        new_instance = EOGroup(
            self.name,
            None,
            variables=eo_vars,
            attrs=copy.deepcopy(self.attrs),
            dims=copy.deepcopy(self.dims),
        )
        root_char = self.path
        self.copy_tree(new_instance, root_char)
        memo[id(self)] = new_instance
        return new_instance

    def copy_tree(self, eo_obj: "EOGroup", root_char: str = "/") -> None:
        """
        Recursively copy the elements of the EOGroup instance to another EOGroup object.

        Parameters
        ----------
        eo_obj : EOGroup
            The EOGroup object to which the elements will be copied.
        root_char : str, optional
            The character to remove from the beginning of paths.
            Default is '/'.

        Returns
        -------
        None

        Notes
        -----
        This method recursively copies all elements (variables and groups) of the current
        EOGroup instance to another EOGroup object (`eo_obj`). The elements are copied
        with their attributes and dimensions. The paths of the elements are adjusted by
        removing the specified root character (`root_char`) and any leading slashes.
        """
        for elem in self.walk():
            elem_path = remove_leading_char(elem.path, root_char)
            elem_path = remove_leading_char(elem_path, "/")
            eo_obj[elem_path] = (
                EOGroup(
                    elem.name,
                    None,
                    variables=None,
                    attrs=copy.deepcopy(elem.attrs),
                    dims=copy.deepcopy(elem.dims),
                )
                if isinstance(elem, EOGroup)
                else copy.deepcopy(elem)
            )

    def __getitem__(self, key: str) -> "EOObject":
        """find and return eovariable or eogroup from the given key.

        Parameters
        ----------
        key: str
            name of the eovariable or eogroup

        Returns
        -------
        EOObject
        """

        if is_absolute_eo_path(key):
            return self.product[product_relative_path(self.path, key)]

        key, subkey = downsplit_eo_path(key)
        # Key is a variable
        if subkey is None and key in self._variables:
            return self._variables[key]
        # Key might be a group
        if key not in self._groups:
            raise KeyError(f"Invalid EOGroup item name {key}")
        item = self._groups[key]
        # Sub group ?
        if subkey is not None:
            if not isinstance(item, EOGroup):
                raise KeyError(f"Item {key}/{subkey} is not a Group")
            return item[subkey]
        return item

    def __setitem__(self, key: str, value: "EOObject") -> None:
        if key == "":
            raise KeyError("Invalid key")
        if is_absolute_eo_path(key):
            self.product[product_relative_path(self.path, key)] = value
            return
        # fixme should probably register the product and path
        key, subkeys = downsplit_eo_path(key)
        if subkeys:
            if key in self._groups:
                sub_container = cast(EOGroup, self[key])
            else:
                sub_container = self._add_local_group(key)
            sub_container[subkeys] = value
            return

        if isinstance(value, EOGroup):
            self._add_local_group(key, value)
        else:
            self._add_local_variable(key, value)

    def __iter__(self) -> Iterator[str]:
        yield from self._groups
        yield from self._variables

    def __delitem__(self, key: str) -> None:
        if is_absolute_eo_path(key):
            raise KeyError("__delitem__ can't take an absolute path as argument")
        if key in self._variables:
            del self._variables[key]
            return
        name, keys = downsplit_eo_path(key)

        if keys is None:
            if name in self._groups:
                del self._groups[name]
        else:
            sub_container = self[name]
            if not isinstance(sub_container, EOGroup):  # sub_container is a EOVariable
                raise KeyError(
                    f"{key} refers to an EOVariable that doesn't support item deletion thought "
                    f"a container ( xarray.DataArray )",
                )
            del sub_container[keys]

    def __len__(self) -> int:
        return len(set(self))

    def _repr_html_(self, prettier: bool = True) -> str:
        """Returns the html representation of the current group displaying the tree.

        Parameters
        ----------
        prettier: str
            Flag for using SVG as label for each Product, Group, Variable, Attribute.
        """
        css_file = EOPF_CPM_PATH / "product/templates/static/css/style.css"

        with css_file.open(mode="r") as css:
            css_content = css.read()

        css_str = f"<style>{css_content}</style>\n"
        rendered_template = renderer("group.html", group=self, prettier=prettier)
        final_str = css_str + rendered_template

        return final_str

    def _print_tree_structure(
        self,
        buffer: List[str],
        group: Union["EOObject", tuple[str, "EOObject"]],
        continues: tuple[bool, ...],
        level: int,
        detailed: bool,
    ) -> None:

        if isinstance(group, tuple):
            group = group[1]
        if not isinstance(group, EOGroup):
            return

        _, pre = EOObject._compute_tree_indents(continues)

        if group.is_root:
            buffer.append(f"{pre}{group.name}")
        else:
            buffer.append(f"{pre}Group({group.name})")

        # Do we print the attributes in case of detailed ?
        if detailed:
            EOGroup._print_details(buffer, group, continues)
        level += 1

        for var, last in is_last(group._variables.values()):
            var._print_tree_structure(buffer, var, continues + (not last,), level, detailed)

        for grp, last in is_last(group._groups.values()):
            self._print_tree_structure(buffer, grp, continues + (not last,), level, detailed)

    @staticmethod
    def _print_details(buffer: List[str], group: "EOGroup", continues: tuple[bool, ...]) -> None:
        # No attrs -> don't add anything
        if len(group.attrs) == 0:
            return

        style = Style()
        fill, _ = EOObject._compute_tree_indents(continues)
        if len(group._variables) != 0 or len(group._groups) != 0:
            buffer.append(f"{fill}{style.cont}Attributes:")
        else:
            buffer.append(f"{fill}{style.end}Attributes:")
        pretty_attrs = pprint.pformat(group.attrs)
        if len(group._variables) != 0 or len(group._groups) != 0:
            buffer.extend([f"{fill}{style.vertical}{line}" for line in pretty_attrs.splitlines()])
        else:
            buffer.extend([f"{fill}{style.empty}{line}" for line in pretty_attrs.splitlines()])

    def to_product(self) -> "EOProduct":
        """Convert this group to a product

        Returns
        -------
        EOProduct
        """
        raise NotImplementedError

    def _init_similar(self) -> "EOGroup":
        attrs = {k: v for (k, v) in self.attrs.items() if k != "_ARRAY_DIMENSIONS"}
        return EOGroup(self.name, attrs=attrs)

    def assign_dims(self, dims: tuple[Hashable, ...]) -> None:
        """Assign dimensions to this object

        Parameters
        ----------
        dims: Iterable[str], optional
            dimensions to assign
        """

        if dims:
            self._attrs[DIMENSIONS_NAME] = dims
        elif not dims and DIMENSIONS_NAME in self._attrs:
            del self._attrs[DIMENSIONS_NAME]

    def __getattr__(self, attr: str) -> Any:
        # this is due to ipython requestion attrs _ipython_canary_method_should_not_exist_
        if attr.startswith("_"):
            return None
        if "short_names" not in attr:
            try:
                return self[attr]
            except KeyError as err:
                raise AttributeError(attr) from err
        raise AttributeError(attr)

    def __contains__(self, key: Any) -> bool:
        direct_key, subkey = downsplit_eo_path(key)
        if direct_key in self._variables:
            return subkey is None

        if direct_key in self._groups:
            if subkey is None:
                return True
            return subkey in self._groups[direct_key]

        return False

    def _recognize_child_group(self, group: "EOGroup", name: str = "") -> None:
        """
        We then have to recognize descenders
        EOGroup
            newly created EOGroup

        Raises
        ------
        EOObjectExistError
            If an object is already a descendant exist at this path.
        """
        if name == "":
            name = group.name
        if name == "":
            raise EOGroupInvalidRequestError("group name can't be empty")
        group._repath(name, self)

    def _add_local_group(self, name: str, group: Optional["EOGroup"] = None, **kwargs: Any) -> "EOGroup":
        """Add a group local to the EOGroup. Does not support paths and recursively adding subgroups.

        Returns
        -------
        EOGroup
            newly created EOGroup

        Raises
        ------
        EOObjectExistError
            If an object already exist at this path.
        """

        if group is None:
            group = EOGroup(name=name, **kwargs)
        new_group_name = name
        if name == "":
            new_group_name = group.name
        if new_group_name == "":
            raise EOGroupInvalidRequestError("group name can't be empty")
        self._recognize_child_group(group, new_group_name)
        # Add it to the memory group list
        self._groups[new_group_name] = group
        group.parent = self
        return group

    def _recognize_child_variable(self, variable: "EOVariable", name: str = "") -> None:
        if name == "":
            name = getattr(variable, "name", "")
        if name == "":
            raise EOGroupInvalidRequestError("variable name can't be empty")
        variable._repath(name, self)

    def _add_local_variable(
        self,
        name: str,
        data: Optional[Any] = None,
        new_eo: bool = True,
        **kwargs: Any,
    ) -> "EOVariable":
        """Add a variable local to the EOVariable. Does not support paths and recursively adding subgroups.

        The given data is copied to create the new EOVariable object.

        Parameters
        ----------
        name: str
            name of the variable to add
        data: any, optional
            data to use for the variable, should be a type accepted by xarray.DataArray
        **kwargs: any
            extra arguments accepted by :obj:`eopf.product.EOVariable`

        Returns
        -------
        EOVariable
            newly created EOVariable

        Raises
        ------
        EOObjectExistError
            If an object already exist at this path.
        InvalidProductError
            If you store a variable locally to a product.
        """

        if name == "":
            name = getattr(data, "name", "")
        if name == "":
            raise EOGroupInvalidRequestError("variable name can't be empty")
        if new_eo:
            if not isinstance(data, EOVariable):
                variable = EOVariable(name=name, data=data, parent=self, **kwargs)
            else:
                variable = EOVariable(name=name, data=data, parent=self, attrs=data.attrs, dims=data.dims, **kwargs)
        else:
            if not isinstance(data, EOVariable):
                variable = EOVariable(name=name, data=data, parent=self, **kwargs)
            else:
                self._recognize_child_variable(data, name)
                variable = data
        self._variables[name] = variable
        variable.parent = self

        return variable

    def compute(self) -> None:
        """
        Recursively compute the variables
        """

        for key, va in self._variables.items():
            self[key] = va.compute()
        for key, gr in self._groups.items():
            gr.compute()

    def persist(self) -> None:
        """
        Recursively persist the variables
        """

        for key, va in self._variables.items():
            self[key] = va.persist()
        for key, gr in self._groups.items():
            gr.persist()

    def export_dask_graph(self, folder: AnyPath) -> None:
        for v in self.variables:
            v[1].graph(folder)
        for g in self.groups:
            g[1].export_dask_graph(folder)

    def walk(self) -> Iterator["EOObject"]:
        """Iterate over all the internal hierarchy of this EOGroup

        After yielding an EOGroup, all the internal hierarchy of this one
        if yield too.

        Yields
        ------
        EOObject
        """

        for value in self.values():
            yield value
            if isinstance(value, EOGroup):
                yield from value.walk()

    @property
    def attrs(self) -> dict[str, Any]:
        """dict[str, Any]: Attributes defined by this object"""
        return self._attrs

    @attrs.setter
    def attrs(self, new_attrs: dict[str, Any]) -> None:
        self._attrs = new_attrs

    @property
    def data(self) -> Any:
        """
        Access to data
        Returns
        -------
        An Xarray dataset build from variables
        """

        data_vars = {}
        coords_vars = {}
        for var_name, var in self.variables:
            data_vars[var_name] = var.data
            for coord_name in var.data.coords:
                if coord_name not in coords_vars:
                    coords_vars[coord_name] = var.data.coords[coord_name]

        ds = Dataset(data_vars=data_vars, coords=coords_vars, attrs=self.attrs)

        return ds

    @property
    def datasize(self) -> int:
        """
        Compute the data size
        Returns
        -------
        data size
        """
        total_size = 0
        for _, var in self.variables:
            total_size += var.datasize
        for _, group in self.groups:
            total_size += group.datasize

        return total_size

    @property
    def groups(self) -> Iterator[tuple[str, "EOGroup"]]:
        """Iterator over the sub EOGroup of this EOGroup"""

        for key, value in self._groups.items():
            yield key, value

    @property
    def variables(self) -> Iterator[tuple[str, "EOVariable"]]:
        """Iterator over the couples variable_name, EOVariable of this EOGroup"""

        for key, value in self._variables.items():
            yield key, value

    def _ipython_key_completions_(self) -> list[str]:  # pragma: no cover
        return list(self.keys())

    @property
    def is_root(self) -> "bool":
        return False

    @staticmethod
    def _keep_var(var_path: str, var_short_name: Optional[str], variables_to_be_kept: List[str]) -> bool:
        """Determine wether a variable should be kept in the subset,
        based on a list of variables to be kept"""

        # variables from coordinates should not be removed
        if var_path.startswith("/coordinates"):
            return True

        # check the var full path
        if var_path in variables_to_be_kept:
            return True

        # check the var short name
        if var_short_name is not None:
            if var_short_name in variables_to_be_kept:
                return True

        return False

    def subset(
        self,
        region: tuple[int, int, int, int],
        reference: Optional[str] = "",
    ) -> "EOGroup":
        """
        Extract a subset

        Parameters
        ----------
        region
        reference

        Returns
        -------

        """

        output = self._init_similar()
        retrieved_data: EOObject
        for n, v in self.variables:
            # subsetting by region
            retrieved_data = v.subset(region, reference=reference)
            if len(retrieved_data) > 0:
                output[n] = retrieved_data
        for n, g in self.groups:
            retrieved_data = g.subset(region, reference)
            if len(retrieved_data) > 0:
                output[n] = retrieved_data
        return output
