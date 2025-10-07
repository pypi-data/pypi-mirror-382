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
merge_attributes_utils.py

merging tool utilities to merge attributes

"""

from datetime import datetime
from logging import Logger
from typing import Any, Tuple

import numpy as np
from shapely import Polygon, unary_union
from xarray import DataTree

from eopf import EOLogging
from eopf.common.date_utils import get_datetime_from_utc
from eopf.product.conveniences import get_default_file_name_no_extension


def general_treatment(key: str, values_key: list[Any]) -> Any | None:
    """
    Get merged output from a list a values
    - if all values arer the same, return this
    - if values are numbers: mean of the values
    - if values are dates: mean of the date
    - if other: no merge

    Parameters
    ----------
    key: name of the parameter
    values_key: list of all key values from inputs zarr to merge

    Returns
    -------
    merged value
    """
    logger = EOLogging().get_logger("eopf.computing.merge_attribute")
    output_value = None

    # if only one value
    if len(values_key) == 1:
        output_value = values_key[0]

    # if list of list, check if they are the same, should not happen
    elif isinstance(values_key[0], list):
        all_identical = all(subvalue == values_key[0] for subvalue in values_key)
        if all_identical:
            output_value = values_key[0]
        else:
            logger.debug(f" {key} can't be merged (list with differences case)")

    else:
        # if all values are the same, we can use set() as we know they are not list
        if len(list(set(values_key))) == 1:
            output_value = values_key[0]

        # if all values are numbers
        elif isinstance(values_key[0], (int, float, complex)):
            output_value = type(values_key[0])(np.mean(np.array(values_key)))

        # if values are string, try date cast
        elif isinstance(values_key[0], str):
            try:
                values_key = [get_datetime_from_utc(value).timestamp() for value in values_key]
                output_value = datetime.fromtimestamp(float(np.mean(np.array(values_key))), tz=None).isoformat()
                output_value = output_value + "Z"
            except ValueError as e:
                logger.debug(f"{key} can't be merged (str case) : {values_key} : {e}")
        else:
            logger.debug(f"   {key} with no merging solution")
    return output_value


def merge_created_attribute(key: str, values_key: list[Any], logger: Logger) -> Any:
    """
    Merge the 'created" attribute in attribute dict
    Parameters
    ----------
    key
    values_key
    logger

    Returns
    -------

    """
    if isinstance(values_key[0], str):
        return datetime.now().isoformat() + "Z"
    return None


def merge_proj_transform(key: str, values_key: list[Any], logger: Logger) -> Any:
    """
    Merge proj transform attributes
    Parameters
    ----------
    key
    values_key
    logger

    Returns
    -------

    """
    if isinstance(values_key[0], list):
        output_value = values_key[0]
        output_value[2] = min(values[2] for values in values_key)
        output_value[5] = max(values[5] for values in values_key)
        return output_value
    logger.debug("proj:transform value is not a list")
    return None


def merge_coordinates(key: str, values_key: list[Any], logger: Logger) -> list[Any] | None:
    """
    Merge coordinates :
    - multi/polygon case => union merge
    - list of string => same values : first list ; different values : None

    Parameters
    ----------
    key: name of the parameter
    values_key: parameter values to merge
    logger: logger

    Returns
    -------
    merge list
    """
    if isinstance(values_key[0][0][0], list):
        #  gather all the polygons in a single list
        polygons = []
        for tile in values_key:
            for poly in np.array(tile):
                polygons.append(Polygon(list(zip(poly[:, 0], poly[:, 1]))))

        # compute union of the multiple geometries
        merged_shape = unary_union(polygons)

        # Type of the results: MultiPolygon/Polygon
        output_value = []
        if merged_shape.geom_type == "MultiPolygon":
            for polygon in merged_shape.geoms:
                output_value.append(np.array([*list(polygon.exterior.coords)]).tolist())
        else:
            output_value = [np.array([*list(merged_shape.exterior.coords)]).tolist()]
        return output_value
    return general_treatment(key, values_key)


def merge_bbox(key: str, values_key: list[Any], logger: Logger) -> Any:
    """
    Merge "bbox" parameter

    Parameters
    ----------
    key: name of the parameter
    values_key: parameter values to merge
    logger: logger

    Returns
    -------
    bottom-right, upper-left points list
    """
    if isinstance(values_key[0][0], (int, float, complex)):
        values_np = np.array(values_key)
        x = values_np[:, [0, 2]].flatten()
        y = values_np[:, [1, 3]].flatten()
        # compute bottom-right, upper-left
        return [max(x), min(y), min(x), max(y)]

    logger.debug("bbox values are not (int, float, complex)")
    return None


def merge_proj_bbox(key: str, values_key: list[Any], logger: Logger) -> Any:
    """
     Merge "proj:bbox" parameter

    Parameters
    ----------
    key: name of the parameter
    values_key: parameter values to merge
    logger: logger

    Returns
    -------
    bottom-left, upper-right points list
    """
    if isinstance(values_key[0][0], (int, float, complex)):
        values_np = np.array(values_key)
        x = values_np[:, [0, 2]].flatten()
        y = values_np[:, [1, 3]].flatten()
        # compute bottom-left, upper-right
        return [min(x), min(y), max(x), max(y)]

    logger.debug("proj:bbox values are not (int, float, complex)")
    return None


def merge_ignore(key: str, values_key: list[Any], logger: Logger) -> Any:
    """
    Ignore merge and only return None

    Parameters
    ----------
    key: name of the parameter
    values_key: parameter values to merge
    logger: logger

    Returns
    -------
    """
    logger.debug(f"   {key} computation is not taken into account")
    return None


def compute_get_image_size_info(dt: DataTree) -> list[Any]:
    """
    Compute output image size by resolution

    Parameters
    ----------
    dt: input datatree

    Returns
    -------
    dict with angles values (degrees)
    """
    image_size = []
    b02 = dt["/measurements/reflectance/r10m/b02"]
    image_size.append(
        {
            "columns": len(b02.x),
            "name": "bands 02, 03, 04, 08",
            "rows": len(b02.y),
            "start_offset": int(b02.x.values[0]),
            "track_offset": int(b02.y.values[0]),
        },
    )

    b05 = dt["/measurements/reflectance/r20m/b05"]
    image_size.append(
        {
            "columns": len(b05.x),
            "name": "bands 05, 06, 07, 8A, 11, 12",
            "rows": len(b02.y),
            "start_offset": int(b05.x.values[0]),
            "track_offset": int(b05.y.values[0]),
        },
    )

    b01 = dt["/measurements/reflectance/r60m/b01"]
    image_size.append(
        {
            "columns": len(b01.x),
            "name": "bands 01, 09, 10",
            "rows": len(b02.y),
            "start_offset": int(b01.x.values[0]),
            "track_offset": int(b01.y.values[0]),
        },
    )
    return image_size


def recompute_s2_l1c_l2a_attributes(dt: DataTree, heavy_compute: bool = False) -> None:
    """
    Compute cloud and snow cover from l1c_classification mask

    Parameters
    ----------
    dt: input datatree

    Returns
    -------
    cloud cover (opaque + cirrus) (%), snow cover (%)
    """
    dt.attrs["stac_discovery"]["id"] = get_default_file_name_no_extension(
        dt.attrs["stac_discovery"]["properties"]["product:type"],
        attributes_dict={str(k): v for k, v in dt.attrs.items()},
    )
    if heavy_compute:
        # angles azimuth/zenith
        zenith_angle, azimuth_angle = compute_sun_angles(dt)
        dt.attrs["other_metadata"]["mean_sun_azimuth_angle_in_deg_for_all_bands_all_detectors"] = azimuth_angle
        dt.attrs["other_metadata"]["mean_sun_zenith_angle_in_deg_for_all_bands_all_detectors"] = zenith_angle
        # cloud and snow cover
        cloud_percentage, snow_percentage = compute_clouds_snow_cover(dt)
        dt.attrs["stac_discovery"]["properties"]["eo:cloud_cover"] = cloud_percentage
        dt.attrs["stac_discovery"]["properties"]["eo:snow_cover"] = snow_percentage

        if "eopf:image_size" in dt.attrs["stac_discovery"]["properties"]:
            dt.attrs["stac_discovery"]["properties"]["eopf:image_size"] = compute_get_image_size_info(dt)


def compute_clouds_snow_cover(dt: DataTree) -> Tuple[float, float]:
    """
    Compute cloud and snow cover from l1c_classification mask

    Parameters
    ----------
    dt: input datatree

    Returns
    -------
    cloud cover (opaque + cirrus) (%), snow cover (%)
    """
    array = dt["/conditions/mask/l1c_classification/r60m"].data_vars["b00"]
    image_length = array.shape[0] * array.shape[1]

    unique, counts = np.unique(array, return_counts=True)
    count_flag = dict(zip(unique, counts))

    flags = array.attrs["flag_masks"]
    flag_meanings = array.attrs["flag_meanings"]

    FLAG_OPAQUE = flags[flag_meanings.index("OPAQUE")]
    FLAG_CIRRUS = flags[flag_meanings.index("CIRRUS")]
    FLAG_SNOW_ICE = flags[flag_meanings.index("SNOW_ICE")]

    count_opaque = count_flag[FLAG_OPAQUE] if FLAG_OPAQUE in count_flag else 0
    count_cirrus = count_flag[FLAG_CIRRUS] if FLAG_CIRRUS in count_flag else 0
    count_snow = count_flag[FLAG_SNOW_ICE] if FLAG_SNOW_ICE in count_flag else 0

    cloud_percentage = (count_opaque + count_cirrus) / image_length * 100
    snow_percentage = count_snow / image_length * 100

    return cloud_percentage, snow_percentage


def compute_sun_angles(dt: DataTree) -> Tuple[float, float]:
    """
    Compute azimuth and zenith angles mean

    Parameters
    ----------
    dt: input datatree

    Returns
    -------
    zenith and azimuth angles (degrees)
    """
    sun_angles_data = dt["/conditions/geometry"].data_vars["sun_angles"]
    type_angles = sun_angles_data.angle
    dict_angles = {}

    for a, angle in enumerate(type_angles):
        dict_angles[angle.values.tolist()] = np.mean(sun_angles_data[a].values)
    return dict_angles["zenith"], dict_angles["azimuth"]
