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
eo_validation.py

EO validation implementation

"""
import os
from dataclasses import dataclass
from enum import Flag, auto
from logging import Logger
from typing import Any, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

import jsonschema
from jsonschema import ValidationError
from pydantic import BaseModel

from eopf import EOContainer, EOGroup, EOProduct, EOVariable
from eopf.common import file_utils
from eopf.common.constants import EOPF_CPM_PATH
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import resolve_path_in_dict

MANDATORY_TOP_ATTR_CATEGORY = ("stac_discovery", "other_metadata")

MANDATORY_STAC_ATTR = (
    "type",
    "stac_version",
    "stac_extensions",
    "id",
    "properties",
    "links",
    "assets",
    "properties/datetime",
    "properties/start_datetime",
    "properties/end_datetime",
    "properties/created",
    "properties/platform",
    "properties/instruments",
    "properties/constellation",
    "properties/mission",
    "properties/processing:version",
    "properties/processing:software",
    "properties/processing:datetime",
    "properties/processing:level",
    "properties/product:type",
    "properties/product:timeliness",
    "properties/sat:absolute_orbit",
    "properties/sat:orbit_state",
)
# STAC CONSTANTS
STAC_ITEM_SCHEMA = "stac_item_schema_v1.1.0.json"
MANDATORY_STAC_EXTENSIONS = ["eopf-stac-extension"]
KEYWORD_TO_EXTENSION = {"eopf": "eopf-stac-extension"}

################################
#  Generic functions
################################

ValidationAnomalyCategories = Literal["STRUCTURE", "STAC", "MODEL"]


class ValidationMode(Flag):
    NONE = 0
    STRUCTURE = auto()
    STAC = auto()
    MODEL = auto()


@dataclass
class AnomalyDescriptor:
    category: ValidationAnomalyCategories
    description: str


def append_to_anomalies(
    out_anomalies: list[AnomalyDescriptor],
    category: ValidationAnomalyCategories,
    reason: str,
    logger: Optional[Logger],
) -> None:
    """
    Append to the anomaly list

    Parameters
    ----------
    out_anomalies
    category
    reason
    logger

    Returns
    -------

    """
    out_anomalies.append(
        AnomalyDescriptor(
            category,
            reason,
        ),
    )
    if logger is not None:
        logger.debug(reason)


############################################
#   Contract validation part
############################################

# -------------------------------------------------------------------------------------------------------------
# ModelValidationMode = Literal["EXACT", "AT_LEAST", "ANY"]
# -> EXACT : must exactly match the model, no extra variable
# -> AT_LEAST: must contains and validate at least the model, extra elements authorized
# -> ANY: Will validate the model constraints on existing elements. an have more or less elements than the model
# -------------------------------------------------------------------------------------------------------------

ModelValidationMode = Literal["EXACT", "AT_LEAST", "ANY"]


class AttributeModel(BaseModel):
    required: bool = True  # attribute must be present


def validate_attrs_against_jsonschema(
    eo_object: Union[EOGroup, EOVariable, EOContainer],
    attrs_jsonschema: Optional[Dict[str, Any]],
    mode: ModelValidationMode,
    out_anomalies: list[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Validate attrs against the schema

    Parameters
    ----------
    eo_object
    attrs_jsonschema
    mode
    out_anomalies
    logger

    Returns
    -------

    """
    if attrs_jsonschema:
        try:
            jsonschema.validate(eo_object.attrs, schema=attrs_jsonschema)
        except ValidationError as e:
            append_to_anomalies(out_anomalies, "MODEL", f"Error validating schema on {e}", logger)


def validate_attrs_against_model(
    eo_object: Union[EOGroup, EOVariable, EOContainer],
    attrs_constraints: Optional[Dict[str, "AttributeModel"]],
    mode: ModelValidationMode,
    out_anomalies: list[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    validate attrs when its a list

    Parameters
    ----------
    eo_object
    attrs_constraints
    mode
    out_anomalies
    logger

    Returns
    -------

    """
    if attrs_constraints is not None:
        for attr_name, constraint in attrs_constraints.items():
            try:
                resolve_path_in_dict(eo_object.attrs, attr_name)
            except KeyError:
                if constraint.required and mode in ("EXACT", "AT_LEAST"):
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Attribute {attr_name} not available in {eo_object.name}",
                        logger,
                    )


############################################
#   STAC validation part
############################################


def check_stac_validity(
    product: EOProduct | EOContainer,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Check if the input product has a valid STAC.
    A generic EOProduct validation is applied for all products.
    What's more, if the product type is defined, a product validation based on the templates data structure
    is also applied.

    Parameters
    ----------
        product (EOProduct): input EOProduct
        validation_mode (str): selected validation mode: possible values
    """
    # STAC metadata check
    stac_utils_folder = os.path.join(EOPF_CPM_PATH.path, "product", "stac_extensions")

    if "stac_discovery" not in product.attrs:
        append_to_anomalies(
            out_anomalies,
            "STAC",
            "No stac_discovery dict in products attributes, cancelling STAC validation",
            logger,
        )
        return

    stac_discovery_data = product.attrs["stac_discovery"]
    if not isinstance(stac_discovery_data, dict):
        append_to_anomalies(
            out_anomalies,
            "STAC",
            "stac_discovery in products attributes is not a dict, cancelling STAC validation",
            logger,
        )
        return

    check_stac_mandatory_list(stac_discovery_data, out_anomalies, logger)
    stac_item = AnyPath(stac_utils_folder) / STAC_ITEM_SCHEMA
    validate_against_jsonschema_file(stac_item, stac_discovery_data, out_anomalies, logger)
    extensions = extract_stac_extensions(stac_discovery_data, logger)
    check_stac_extensions_list(stac_discovery_data, extensions, out_anomalies, logger)
    # Validate STAC metadata with the stac item standard schema + possible STAC extensions
    check_stac_schemas_validity(stac_discovery_data, extensions, stac_utils_folder, out_anomalies, logger)
    # Additional checks implicit on STAC:
    check_stac_geometry(stac_discovery_data, out_anomalies, logger)


def extract_stac_extensions(
    product_stac_dict: Dict[str, Any],
    logger: Optional[Logger],
) -> Dict[str, Tuple[str, str, str]]:
    """
    Check if all mandatory STAC extensions are listed in the stac_extension list


    Check also that all properties keyword are linked to its extension in the list

    Parameters
    ----------
        product_stac_dict (dict): stac_discovery metadata of the product
        path_to_stac_data (str): path to STAC standard schema and extensions
    """
    res: Dict[str, Tuple[str, str, str]] = {}
    if "stac_extensions" in product_stac_dict:
        for url in product_stac_dict["stac_extensions"]:
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            name = parts[-3]  # 'eopf-stac-extension'
            version = parts[-2]  # v1.2.0
            res[name] = (name, version, url)

    return res


def check_stac_mandatory_list(
    product_stac_dict: dict[str, Any],
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Chack that list of mandatory stac extension is in the attrs

    Parameters
    ----------
    product_stac_dict
    out_anomalies
    logger

    Returns
    -------

    """
    for p in MANDATORY_STAC_ATTR:
        try:
            resolve_path_in_dict(product_stac_dict, p)
        except KeyError:
            append_to_anomalies(
                out_anomalies,
                "STAC",
                f"STAC attributes {p} not found in STAC metadatas",
                logger,
            )


def check_stac_extensions_list(
    product_stac_dict: dict[str, Any],
    extensions: Dict[str, Tuple[str, str, str]],
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Validate that used extension are in the stac list,
    validates that stac extension for used attr are here also

    Parameters
    ----------
    product_stac_dict
    extensions
    out_anomalies
    logger

    Returns
    -------

    """
    for ext in MANDATORY_STAC_EXTENSIONS:
        if ext not in extensions:
            append_to_anomalies(
                out_anomalies,
                "STAC",
                f"Mandatory extension {ext} not listed in stac_extensions",
                logger,
            )
    check_stac_extension_usage(product_stac_dict, extensions, out_anomalies, logger)


def check_stac_extension_usage(
    product_stac_dict: dict[str, Any],
    extensions: Dict[str, Tuple[str, str, str]],
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """

    Parameters
    ----------
    product_stac_dict
    extensions
    out_anomalies
    logger

    Returns
    -------

    """
    # For each attribute, check if the latter is linked to a STAC extension, if yes
    # load the associated json schema of the extension and validate the STAC attribute according
    # to this schema
    used_extension_list = []
    for key, _ in product_stac_dict.items():
        # STAC extension validation
        if key == "properties":
            for prop_key, _ in product_stac_dict[key].items():
                if ":" in prop_key:
                    extension = prop_key.split(":")[0]
                    extension = KEYWORD_TO_EXTENSION.get(extension, extension)
                    used_extension_list.append(extension)
    ext_to_search = list(sorted(set(used_extension_list)))
    for ext in ext_to_search:
        if ext not in extensions:
            append_to_anomalies(
                out_anomalies,
                "STAC",
                f"Extension {ext} used in properties but not listed in stac_extensions",
                logger,
            )
    for ext in extensions:
        if ext not in ext_to_search:
            append_to_anomalies(
                out_anomalies,
                "STAC",
                f"Extension {ext} listed in stac_extensions but not used",
                logger,
            )


def check_stac_geometry(
    product_stac_dict: dict[str, Any],
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """

    Parameters
    ----------
    product_stac_dict
    extensions
    out_anomalies
    logger

    Returns
    -------

    """
    if "geometry" in product_stac_dict:
        if "type" in product_stac_dict["geometry"]:
            if product_stac_dict["geometry"]["type"] == "Polygon":
                for idx, linear_ring in enumerate(product_stac_dict["geometry"]["coordinates"]):
                    if not linear_ring[0] == linear_ring[-1]:
                        append_to_anomalies(
                            out_anomalies,
                            "STAC",
                            f"Linear ring {idx} in polygon is not closed",
                            logger,
                        )


def check_stac_schemas_validity(
    product_stac_dict: dict[str, Any],
    extensions: Dict[str, Tuple[str, str, str]],
    path_to_stac_data: str,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """Check that all elements from the STAC data follow the STAC standards (and STAC extensions)
    Check if STAC metadata of the input product have a valid format
    Links to the STAC item specifications:
    https://github.com/radiantearth/stac-spec/blob/master/item-spec/item-spec.md#item-fields

    Corresponding jsonschema:
    https://github.com/radiantearth/stac-spec/blob/master/item-spec/json-schema/item.json

    Parameters
    ----------
        product_stac_dict (dict): stac_discovery metadata of the product
        path_to_stac_data (str): path to STAC standard schema and extensions
    """
    for name, version, url in extensions.values():
        extension_local = AnyPath(path_to_stac_data) / "extensions" / f"{name}_{version}.json"
        if not extension_local.exists():
            if logger is not None:
                logger.warning(f"Extension {extension_local.path} doesn't exist in the CPM extension folder")
            extension_local = AnyPath(url)
        validate_against_jsonschema_file(extension_local, product_stac_dict, out_anomalies, logger)


def validate_against_jsonschema_file(
    extension_file_to_validate: AnyPath,
    attrs_dict: dict[str, Any],
    out_anomalies: list[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    validate stac dict

    Parameters
    -----------
    extension_file_to_validate: AnyPath
    attrs_dict: dict[str, Any]
    out_anomalies: list[AnomalyDescriptor]
    logger: Logger

    """
    try:
        ext = file_utils.load_json_file(extension_file_to_validate)
    except FileNotFoundError:
        append_to_anomalies(out_anomalies, "STAC", f"Extension {extension_file_to_validate.path} not found !!!", logger)
        return
    try:
        jsonschema.validate(attrs_dict, ext)
    except ValidationError as e:
        append_to_anomalies(
            out_anomalies,
            "STAC",
            f"Error validating STAC metadata with extension {extension_file_to_validate.path}: {e}",
            logger,
        )


###############################
# COMMON CHECKS
###############################


def check_attributes_top_category(
    product: EOProduct | EOContainer,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    # Check mandatory attribute categories exist in the EOProduct
    if any(key not in product.attrs for key in MANDATORY_TOP_ATTR_CATEGORY):
        append_to_anomalies(
            out_anomalies,
            "STRUCTURE",
            f"Missing top-level attribute category from the mandatory list: {MANDATORY_TOP_ATTR_CATEGORY}",
            logger,
        )
