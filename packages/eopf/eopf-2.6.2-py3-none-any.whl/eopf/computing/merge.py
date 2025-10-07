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
merge.py

Merging tool to merge multiple xarray zarr datasets

For example S2 L1C tiles

"""
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypedDict

import numpy as np
import xarray as xr
from xarray import Dataset, DataTree, open_datatree

from eopf import EOLogging
from eopf.computing.merge_attributes import fun_combine_attrs, recompute_attributes
from eopf.exceptions.errors import MergingError

if TYPE_CHECKING:
    from xarray.core.datatree import DatasetView

# Keyword arguments for xarray.open_dataset
OpenDatasetKwargs = TypedDict(
    "OpenDatasetKwargs",
    {
        "chunks": dict[str, int],
        "engine": str,
        "drop_variables": list[str],
    },
)
# Keyword arguments for merging xarray datasets
MergeKwargs = TypedDict(
    "MergeKwargs",
    {
        "compat": Literal["identical", "override"],
        "fill_value": dict[str, Any] | None,
        "combine_attrs": Callable[[Any, Any], list[Any] | Any | None],
    },
)

GROUPS_TO_SKIP: list[str] = [
    "/conditions/meteo",  # L1
    "/conditions/meteorology/cams",  # L2
    "/conditions/meteorology/ecmwf",  # L2
]
NON_SPATIAL_GROUPS = [
    "/conditions/meteo",  # L1
    "/conditions/meteorology/cams",  # L2
    "/conditions/meteorology/ecmwf",  # L2
]

OPEN_DATASET_KWARGS: OpenDatasetKwargs = {
    "chunks": {},
    "engine": "zarr",
    "drop_variables": [
        "mean_vaa",  # L1
        "mean_vza",  # L1
        "mean_sun_angles",  # L2
        "mean_viewing_incidence_angles",  # L2
    ],  # TODO: drop o re-compute after combining all tiles?
}
UINT_NAN = 0  # Placeholder fill value for unsigned integer types
GEOMETRY_GROUP = "/conditions/geometry"
# Attributes to ignore when comparing metadata
INCONSISTENT_ATTRS = [
    "other_metadata",
    "other_metadata4",
    "stac_discovery",
    "coordinates",
    "proj:bbox",
    "proj:transform",
    "sun_angles",
    "proj:shape",
]


def _get_spatial_coords(ds: Dataset) -> list[str]:
    """
    Extracts spatial coordinates from a dataset.

    Parameters
    ----------
    ds : Dataset
        Input dataset.

    Returns
    -------
    list[str]
        List of spatial coordinate names (e.g., ["x10", "y10"]).
    """
    return [coord for coord in ds.coords if isinstance(coord, str) and coord.startswith(("x", "y"))]


def _find_slicers(paths: list[str]) -> dict[str, dict[str, slice]]:
    """
    Determines spatial slices for each tile based on its coordinates.

    Parameters
    ----------
    paths : list[str]
        List of Zarr tile paths.

    Returns
    -------
    dict[str, dict[str, slice]]
        Mapping from tile path to spatial slicing bounds.
    """
    # Concat the tiles into a single dataset
    tiles = _open_tiles(paths)
    ds = xr.concat(tiles, "tile")
    slicers = {}
    for ds_tile in tiles:
        path = ds_tile["tile"].item()
        ds_tile = ds_tile.squeeze("tile")
        slicer = {}
        for coord in _get_spatial_coords(ds_tile):
            size = ds_tile[f"{coord}_bounds"].diff("bounds")
            bounds = list(ds_tile[f"{coord}_bounds"].values)
            for label in ("upper", "lower"):
                # Ignored type as it doesn't detect that we have upper and lower literal
                diff = ds[coord].diff(coord, label=label)
                try:
                    distance = diff.sel({coord: ds_tile[coord]})
                except KeyError:
                    continue
                else:
                    if distance >= size:
                        continue
                    shift = (size - distance).item() / 2
                    if label == "lower":
                        bounds[1] -= shift + 0.5  # exclusive
                    else:
                        bounds[0] += shift  # inclusive
            slicer[coord[0]] = slice(*bounds)
        slicers[path] = slicer
    return slicers


def _open_tiles(paths: list[str]) -> list[Dataset]:
    """
    Open the tiles and sort data by coordinates
    Parameters
    ----------
    paths : path to tiles

    Returns
    -------
    (combined_dataset, list(tile datasets))

    """
    tiles = []
    for path in paths:
        # Open the geometry group of the dataset to get spatial bounds
        ds = xr.open_dataset(path, group=GEOMETRY_GROUP, **OPEN_DATASET_KWARGS)
        coords = _get_spatial_coords(ds)
        # Select endpoints and sort by coordinates for bounds calculation
        ds = ds[coords].isel({coord: [0, -1] for coord in coords}).sortby(coords)
        variables = {}
        for coord in coords:
            variables[coord] = ds[coord].mean(coord, keepdims=True)
            variables[f"{coord}_bounds"] = xr.DataArray(ds[coord].values, dims="bounds")
        ds = xr.Dataset(variables)
        tiles.append(ds.expand_dims(tile=[path]))
    return tiles


def _preprocess(ds: Dataset, slicers: dict[str, dict[str, slice]]) -> Dataset:
    """
    Applies spatial slicing and sorting to a dataset.

    Parameters
    ----------
    ds : Dataset
        The dataset to preprocess.
    slicers : dict[str, dict[str, slice]]
        Slicers per tile path and coordinate.

    Returns
    -------
    Dataset
        Preprocessed dataset.
    """
    path = ds.encoding["source"]
    indexers = {dim: slicer for dim in ds.dims if isinstance(dim, str) and (slicer := slicers[path].get(dim[0]))}
    return ds.sortby(list(indexers)).sel(indexers)


# ----------------------------------------
# Main Tile-Combining Function
# ----------------------------------------


def open_and_combine_tiles(input_dir: str, allow_missing_tiles: bool = False, update_mode: bool = True) -> DataTree:
    """
    Opens and combines multiple spatial tiles into a single hierarchical DataTree.

    Parameters
    ----------

    input_dir : str
        Path to a directory containing Zarr tiles.
    allow_missing_tiles : bool
        Whether to allow missing data and fill with defaults.
    update_mode: bool
        Whether or not recompute the attributes


    Returns
    -------
    DataTree
        Combined data structure of all tiles.
    """
    logger = EOLogging().get_logger("eopf.computing.merge")
    logger.info(f"Searching for products in {input_dir}")
    logger.info(f"Allow missing tiles: {allow_missing_tiles}")
    paths = list(map(str, Path(input_dir).absolute().iterdir()))
    logger.debug(f"{len(paths)} products found")
    slicers = _find_slicers(paths)

    sample_dict = open_datatree(paths[0], **OPEN_DATASET_KWARGS).to_dict()
    output_dict: dict[str, Dataset] = {}
    for group, ds in sample_dict.items():
        if group in GROUPS_TO_SKIP:
            continue

        if group in NON_SPATIAL_GROUPS:
            _merge_non_spatial_groups(ds, group, output_dict, paths, allow_missing_tiles)
            continue

        # Preprocess all tiles for this group to apply slicing
        tiles = [
            _preprocess(
                xr.open_dataset(path, group=group, **OPEN_DATASET_KWARGS),
                slicers,
            )
            for path in paths
        ]
        # Define merge options
        merge_kwargs: MergeKwargs = {
            "compat": "identical",
            "fill_value": (
                {
                    var: np.array(UINT_NAN if da.dtype.kind == "u" else np.nan, da.dtype)
                    for var, da in ds.data_vars.items()
                }
                if allow_missing_tiles
                else None
            ),
            "combine_attrs": lambda tiles, context: fun_combine_attrs(tiles, {}),
        }
        ds = _merge_group(ds, tiles, merge_kwargs)
        # Apply chunking for efficient storage
        chunks = {}
        for da in ds.data_vars.values():
            chunks.update(da.encoding["preferred_chunks"])
        output_group = ds.chunk(chunks)
        output_dict[group] = output_group

    dt = DataTree.from_dict(output_dict)
    dt = recompute_attributes(dt, heavy_compute=update_mode)

    return dt


def _merge_group(ds: Dataset, tiles: list[Dataset], merge_kwargs: MergeKwargs) -> Dataset:
    """
    Merge the tiles together in a single dataset

    Parameters
    ----------
    ds
    tiles
    allow_missing_tiles

    Returns
    -------

    """

    # Process each resolution separately
    # Merge scalar variables (non-spatial)
    spatial_coords = _get_spatial_coords(ds)
    datasets = [xr.merge([tile.drop_dims(spatial_coords, errors="ignore") for tile in tiles], **merge_kwargs)]
    # Merge spatial variables, grouped by resolution
    for suffix in {coord[1:] for coord in spatial_coords}:
        dims_to_drop = [coord for coord in spatial_coords if not coord[1:] == suffix]
        ds_combined = xr.combine_by_coords(
            [tile.drop_dims(dims_to_drop, errors="ignore") for tile in tiles],
            **merge_kwargs,
            data_vars="minimal",
            coords="minimal",
        )
        if not isinstance(ds_combined, Dataset):
            raise MergingError("Combined data is not an Xarray dataset")
        datasets.append(ds_combined)
    ds = xr.merge(datasets, **merge_kwargs)

    return ds


def _merge_non_spatial_groups(
    ds: Dataset,
    group: str,
    output_dict: dict[str, Dataset],
    paths: list[str],
    allow_missing_tiles: bool,
) -> None:
    # Preprocess all tiles for this group to apply slicing
    tiles_groups = [xr.open_dataset(path, group=group, **OPEN_DATASET_KWARGS) for path in paths]
    # Define merge options
    merge_kwargs_sparse: MergeKwargs = {
        "compat": "override",
        "fill_value": (
            {var: np.array(UINT_NAN if da.dtype.kind == "u" else np.nan, da.dtype) for var, da in ds.data_vars.items()}
            if allow_missing_tiles
            else None
        ),
        "combine_attrs": lambda tiles, context: fun_combine_attrs(tiles, {}),
    }
    # Merge scalar variables (non-spatial)
    datasets = [xr.merge(tiles_groups, **merge_kwargs_sparse)]
    ds = xr.merge(datasets, **merge_kwargs_sparse)
    # Apply chunking for efficient storage
    chunks = {}
    for da in ds.data_vars.values():
        chunks.update(da.encoding["preferred_chunks"])
    output_dict[group] = ds.chunk(chunks)


# ----------------------------------------
# Sanity Check
# ----------------------------------------


def _sanity_check(path: Path, dt: DataTree) -> None:
    """
    Internal: checks if a single tile matches its representation in the DataTree.

    Parameters
    ----------
    path : Path
        Path to the original tile.
    dt : DataTree
        Combined DataTree.
    """
    dt_tile = open_datatree(path, engine="zarr")
    for group, ds_tile in dt_tile.to_dict().items():
        if group in GROUPS_TO_SKIP:
            if group in dt.groups:
                raise MergingError(f"{group} is already in the dataset")
            continue

        # Variables
        ds: DatasetView = dt[group].dataset
        if not set(ds.dims) == set(ds_tile.dims):
            raise MergingError("Dataset dims doesn't match tile dims")

        if not set(ds.coords) == set(ds_tile.coords):
            raise MergingError("Dataset coordinates doesn't match tile coordinates")

        if not set(ds.data_vars) == set(ds_tile.data_vars) - set(OPEN_DATASET_KWARGS["drop_variables"]):
            raise MergingError("Data vars are not aligned")

        # Resolution
        if group != GEOMETRY_GROUP:
            _sanity_check_resolution(ds, group)

        # Attributes
        _sanity_check_attributes(ds, ds_tile)

        # Variables
        _sanity_check_variables(ds, ds_tile)


def _sanity_check_attributes(ds: "DatasetView", ds_tile: Dataset) -> None:
    ds_attrs_attrs_cons = {k: v for k, v in ds.attrs.items() if k not in INCONSISTENT_ATTRS}
    to_compare = {k: v for k, v in ds_tile.attrs.items() if k not in INCONSISTENT_ATTRS}
    if not ds_attrs_attrs_cons == {k: v for k, v in ds_tile.attrs.items() if k not in INCONSISTENT_ATTRS}:
        raise MergingError(f"{ds_attrs_attrs_cons} != {to_compare} ")


def _sanity_check_variables(ds: "DatasetView", ds_tile: Dataset) -> None:
    for var, da in ds.variables.items():
        da_tile = ds_tile[var]
        if not da.dtype == da_tile.dtype:
            raise MergingError("Dtype doesn't match")
        da_attrs_attrs_cons = {k: v for k, v in da.attrs.items() if k not in INCONSISTENT_ATTRS}
        if not da_attrs_attrs_cons == {k: v for k, v in da_tile.attrs.items() if k not in INCONSISTENT_ATTRS}:
            raise MergingError("Inconsistent attributes")


def _sanity_check_resolution(ds: "DatasetView", group: str) -> None:
    for dim in ds.dims:
        if not isinstance(dim, str) or dim[0] not in ("x", "y"):
            continue
        (delta,) = set(ds[dim].diff(dim).values)
        digits = "".join([s for s in dim if s.isdigit()] or [s for s in group.rsplit("/")[-1] if s.isdigit()])
        if not delta == int(digits):
            raise MergingError("Resolution doesn't match")


def sanity_check(input_dir: str, dt: DataTree | None = None) -> None:
    """
    Runs sanity checks to validate that combined DataTree matches individual tiles.

    Parameters
    ----------
    input_dir : str
        Path to directory containing tiles.
    dt : DataTree | None
        Optional precomputed DataTree. If None, it will be recomputed.
    """
    if dt is None:
        dt = open_and_combine_tiles(input_dir)
    for path in Path(input_dir).iterdir():
        _sanity_check(path, dt)
