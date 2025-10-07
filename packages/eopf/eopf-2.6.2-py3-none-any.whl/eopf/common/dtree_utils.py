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
dtree_utils.py

datatree utils

"""
from typing import Any, Dict, cast

import xarray as xr
import zarr
from xarray.core.datatree import DataTree

from eopf.common.file_utils import AnyPath
from eopf.product.conveniences import get_default_file_name_no_extension


def create_dtree_from_zarr_group(zarr_group: zarr.Group, name: str, **kwargs: Any) -> DataTree:
    """Constructs a DataTree from a given Zarr group

    Parameters
    ----------
    zarr_group: zarr.Group
        The root Zarr group from which the DataTree will be constructed.
        A Zarr group is a collection of arrays and nested groups.
    name: str
        The name to be assigned to the root node of the DataTree.
    kwargs: Any
        Additional keyword arguments passed to xr.open_dataset

    Returns
    -------
    DataTree
        The constructed DataTree object with nodes corresponding to datasets and groups within the Zarr hierarchy.
    """

    def create_tree_from_group(group: zarr.Group, node_path: AnyPath, **kwargs: Any) -> DataTree:
        """Recursive function that performs the construction of the DataTree by traversing the Zarr group hierarchy.

        Parameters
        ----------:
        group: zarr.Group
            The current Zarr group being processed
        path: str, optional
            The path within the Zarr hierarchy for the current group

        Returns
        -------
        DataTree:
            A subtree corresponding to the current Zarr group, with child nodes for each nested group or dataset.
        """
        try:
            ds = xr.open_dataset(group.store, group=group.path, engine="zarr", **kwargs)
        except ValueError:  # Handle the case where the group does not contain a dataset
            ds = xr.Dataset()

        node: DataTree = DataTree(
            name=node_path.basename if node_path.original_url else name,
            dataset=ds,
        )

        for key, value in group.groups():
            node_subpath = (
                AnyPath(f"{node_path.original_url}{node_path.sep}{key}") if node_path.original_url else AnyPath(key)
            )
            child_node = create_tree_from_group(value, node_subpath, **kwargs)
            node[key] = child_node

        return node

    root_node_path = AnyPath("")
    return create_tree_from_group(zarr_group, root_node_path, **kwargs)


def open_datatree(produt_anypath: AnyPath, product_id: str, **kwargs: Any) -> DataTree:
    """Open and decode a EOPF-like Zarr product

    Parameters
    ----------
    produt_anypath: AnyPath
        Path to directory in file system or name of zip file (as an AnyPath object)
    product_id: str
        Id of the product as passed in the payload
    kwargs:
        any parameters passed to xarray dtree

    Returns
    -------
        DataTree
    """

    zarr_store = produt_anypath.filesystem.get_mapper(produt_anypath.path)
    # Open the Zarr root group
    root_group = zarr.open_group(zarr_store, mode="r")

    # Create the DataTree from the Zarr root group
    data_tree = create_dtree_from_zarr_group(root_group, product_id, **kwargs)

    return data_tree


def write_datatree(eo_data: DataTree, output_anypath: AnyPath, **kwargs: Any) -> None:
    """
    Write a datatree to zarr
    """
    used_kwargs = kwargs.copy()
    used_kwargs.setdefault("consolidated", True)
    used_kwargs.setdefault("mode", "w")
    # remove storage options if any provided
    used_kwargs.pop("storage_options", None)
    eo_data.to_zarr(store=output_anypath.to_zarr_store(), **used_kwargs)


def get_default_file_name_datatree(eo_data: DataTree) -> str:
    """
    Get the default filename as per PDFS convention on a datatreee
    Should only be used in triggering when datatree activated

    Parameters
    ----------
    eo_data

    Returns
    -------

    """

    # TODO: mission specific for datatree
    mission_specific = None
    product_type = eo_data.attrs["stac_discovery"]["properties"]["product:type"]
    return (
        get_default_file_name_no_extension(
            product_type,
            cast(Dict[str, Any], eo_data.attrs),
            mission_specific=mission_specific,
        )
        + ".zarr"
    )
