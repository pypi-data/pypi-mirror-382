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
conveniences.py

convenience functions for product module

"""

import warnings
from collections import namedtuple
from typing import TYPE_CHECKING, Any, Optional, Union

from eopf.common import date_utils
from eopf.common.functions_utils import compute_crc
from eopf.exceptions import StoreMissingAttr

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_container import EOContainer
    from eopf.product.eo_product import EOProduct


def init_product(
    product_name: str,
    **kwargs: Any,
) -> "EOProduct":
    """Convenience function to create a valid EOProduct base.

    Parameters
    ----------
    product_name: str
        name of the product to create
    **kwargs: any
        Any valid named arguments for EOProduct

    Returns
    -------
    EOProduct
        newly created product

    See Also
    --------
    eopf.product.EOProduct
    eopf.product.EOProduct.is_valid
    """
    # lazy import for circular deps
    from eopf.product.eo_product import EOProduct

    warnings.warn("Deprecated, use EOProduct.init_product instead")
    return EOProduct.init_product(product_name=product_name, **kwargs)


def get_product_type(eo_obj: Union["EOProduct", "EOContainer"]) -> Optional[str]:
    """Convenience function to retrieve product:type from EOProduct/EOContainer

    Parameters
    ----------
    eo_obj: Union[EOProduct, EOContainer]
        product or container

    Returns
    -------
    Optional[str]
        product_type

    """
    warnings.warn("Deprecated : use product.product_type instead", DeprecationWarning)
    try:
        return eo_obj.attrs["stac_discovery"]["properties"]["product:type"]
    except KeyError:
        return None


def set_product_type(eo_obj: Union["EOProduct", "EOContainer"], intype: Optional[str]) -> None:
    """Convenience function to retrieve product:type from EOProduct/EOContainer

    Parameters
    ----------
    eo_obj: Union[EOProduct, EOContainer]
        product or container
    type: str
        product:type

    """
    warnings.warn("Deprecated : use product.product_type instead", DeprecationWarning)
    eo_obj.attrs.setdefault("stac_discovery", {}).setdefault("properties", {})["product:type"] = intype


FilenameProperties = namedtuple(
    "FilenameProperties",
    ["start_datetime", "end_datetime", "platform_unit", "relative_orbit", "timeliness_category"],
)


def get_default_file_name_no_extension(
    product_type: str,
    attributes_dict: dict[str, Any],
    mission_specific: Optional[str] = None,
) -> str:
    """
    get the default filename using the convention :
    - Take product:type or internal product_type (9 characters, see #97)
    - Add "_"
    - Take start_datetime as YYYYMMDDTHHMMSS
    - Add "_"
    - Take end_datetime and start_datetime and calculate the difference in seconds (between 0000 to 9999)
    - Add "_"
    - Take the last character of "platform"  (A or B)
    - Take sat:relative_orbit (between 000 and 999)
    - Add "_"
    - Take product:timeline: if it is NRT add "T";  if it is STC add "_" ; if it is NTC, add "S"
    - Generate a Hexadecimal CRC on 3 characters
    if mission specific provided :
    - Add "_"
    - Add <mission_specific>
    """

    properties = _get_properties_for_file_name(attributes_dict)

    # get the product type
    if product_type is None or product_type == "":
        raise StoreMissingAttr("Missing product type and product:type attributes")

    start_datetime_str = date_utils.get_date_yyyymmddthhmmss_from_tm(
        date_utils.get_datetime_from_utc(properties.start_datetime),
    )

    duration_in_second = int(
        (
            date_utils.get_datetime_from_utc(properties.end_datetime)
            - date_utils.get_datetime_from_utc(properties.start_datetime)
        ).total_seconds(),
    )
    if duration_in_second > 9999:
        warnings.warn("Maximum sensing duration exceeded, putting 9999 in name")
        duration_in_second = 9999

    timeline_tag = "X"
    if properties.timeliness_category in ["NR", "NRT", "NRT-3h"]:
        timeline_tag = "T"
    elif properties.timeliness_category in ["ST", "24H", "STC", "Fast-24h", "AL"]:
        timeline_tag = "_"
    elif properties.timeliness_category in ["NTC", "NT"]:
        timeline_tag = "S"
    else:
        raise StoreMissingAttr(
            "Unrecognized product:timeliness_category attribute, should be NRT/24H/STC/NTC",
        )
    crc = compute_crc(attributes_dict, digits=3)
    if mission_specific is not None:
        mission_specific = f"_{mission_specific}"
    else:
        mission_specific = ""
    filename = (
        f"{product_type}_{start_datetime_str}_{duration_in_second:04d}_"
        f"{properties.platform_unit}{properties.relative_orbit:03d}_"
        f"{timeline_tag}{crc}{mission_specific}"
    )
    return filename


def _get_properties_for_file_name(attributes_dict: dict[str, Any]) -> FilenameProperties:
    try:
        props = attributes_dict["stac_discovery"]["properties"]
        timeliness_category = props.get("product:timeliness_category")
        if not timeliness_category:
            raise StoreMissingAttr("Missing product:timeliness_category attr")

        return FilenameProperties(
            start_datetime=props["start_datetime"],
            end_datetime=props["end_datetime"],
            platform_unit=props["platform"][-1].upper(),
            relative_orbit=props["sat:relative_orbit"],
            timeliness_category=timeliness_category,
        )
    except KeyError as exc:
        raise StoreMissingAttr("Missing properties in product to generate default filename") from exc


# -----------------------------------------------
