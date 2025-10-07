from logging import Logger
from typing import Any

from xarray import DataTree

from eopf import EOLogging
from eopf.computing.merge_attributes_utils import (
    general_treatment,
    merge_bbox,
    merge_coordinates,
    merge_created_attribute,
    merge_ignore,
    merge_proj_bbox,
    merge_proj_transform,
    recompute_s2_l1c_l2a_attributes,
)

# Dict to map a key to a specific handling function
SPECIFIC_ATTRS_HANDLERS_DICT = {
    "proj:transform": merge_proj_transform,
    "bbox": merge_bbox,
    "proj:bbox": merge_proj_bbox,
    "created": merge_created_attribute,
    "coordinates": merge_coordinates,
    "history": merge_ignore,
    "proj:wkt2": merge_ignore,
}


def fun_combine_attrs(tiles_attrs: list[Any], context: dict[Any, Any] | None) -> list[Any] | Any | None:
    """
    Customized fonction to merge attributes

    Parameters
    ----------
    @param tiles_attrs: dict values
    @param context: context, first dict values if that case

    Returns
    -------
    merged dict
    """
    logger = EOLogging().get_logger("eopf.computing.merge_attribute")
    output = {}

    # if there is only one value to merge
    if len(tiles_attrs) == 1:
        return tiles_attrs[0]

    for key in tiles_attrs[0]:

        # if param is a dict, recursive iteration over it
        if isinstance(tiles_attrs[0][key], dict):
            output[key] = fun_combine_attrs([attr[key] for attr in tiles_attrs], context)
            continue
        try:
            values_key = [tile_attr[key] for tile_attr in tiles_attrs]
        except KeyError:
            logger.debug(f"   {key} is not present in all the tiles; skipping")
            continue

        _handle_single_attr(key, values_key, output, context, logger)

    return output


def _handle_single_attr(
    key: str,
    values_key: list[Any],
    output: dict[Any, Any],
    context: dict[Any, Any] | None,
    logger: Logger,
) -> None:
    # Only one value, don't bother
    if len(values_key) == 1:
        output[key] = values_key[0]
        return
    # if key need a specific treatment
    if key in SPECIFIC_ATTRS_HANDLERS_DICT:
        output[key] = SPECIFIC_ATTRS_HANDLERS_DICT[key](key, values_key, logger)
        return
    # if values are numeric or string
    if not isinstance(values_key[0], list):
        output[key] = general_treatment(key, values_key)
        return
    # Handle sub element treatment
    new_val = _fun_combine_sub_attrs(key, values_key, context)
    if new_val is not None:
        output[key] = new_val
        return
    logger.error(f"   {key} error : no attr merging method found")


def _fun_combine_sub_attrs(key: str, values_key: list[Any], context: dict[Any, Any] | None) -> Any:
    logger = EOLogging().get_logger("eopf.computing.merge_attribute")
    # if values are another list
    # if values are list of numerical/string, they should all be identical
    # as we don't know the way to handle differences
    if isinstance(values_key[0][0], (str, int, float, complex, list)):

        all_identical = all(sublist == values_key[0] for sublist in values_key)
        if all_identical:
            return values_key[0]
        logger.debug(f"{key} can't be naively merged : different values found")
        return []

    # if values are list of dict
    if isinstance(values_key[0][0], dict):
        new_value = []
        for b in range(len(values_key[0])):
            new_value.append(fun_combine_attrs([key_[b] for key_ in values_key], context))
        return new_value

    return None


PRODUCT_TYPE_RECOMP_ATTR_DICT = {
    "S02MSIL1C": recompute_s2_l1c_l2a_attributes,
    "S02MSIL2A": recompute_s2_l1c_l2a_attributes,
}


def recompute_attributes(dt: DataTree, heavy_compute: bool = False) -> DataTree:
    """
    Update attribute with merged data

    Parameters
    ----------
    dt: DataTree
    heavy_compute: if recompute parameters

    Returns
    -------
    new DataTree with updated attributes
    """

    # general information not depending on the product type
    dt.attrs["stac_discovery"]["id"] = "TODO"  # todo

    PRODUCT_TYPE_RECOMP_ATTR_DICT.get(
        dt.attrs["stac_discovery"]["properties"]["product:type"],
        lambda b, heavy_compute: b,
    )(dt, heavy_compute)

    return dt
