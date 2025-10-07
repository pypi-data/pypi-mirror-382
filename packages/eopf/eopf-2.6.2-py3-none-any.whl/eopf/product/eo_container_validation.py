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
eo_container_validation.py

EOContainer validation implementation

"""
import re
from logging import Logger
from typing import Any, Callable, Dict, List, Optional, Tuple

from pydantic import BaseModel

from eopf import EOConfiguration, EOContainer, EOLogging
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.common.functions_utils import get_all_paths_in_dict, nested_dict_from_paths
from eopf.product.eo_product import EOProduct
from eopf.product.eo_product_validation import (
    EOProductModel,
    check_coherent_dimension_product,
    check_eoproduct_validity,
    check_product_model_validity,
    model_to_product,
    product_to_model,
    validate_product_against_model,
)
from eopf.product.eo_validation import (
    AnomalyDescriptor,
    AttributeModel,
    ModelValidationMode,
    ValidationMode,
    append_to_anomalies,
    check_attributes_top_category,
    check_stac_validity,
    validate_attrs_against_jsonschema,
    validate_attrs_against_model,
)

# ------------------------------------ EOCONTAINER validation rules ------------------------------------

# ---------- Summary of the workflow for container validation


# ---------- Validation for top-level attributes in an EOContainer

# * STAC metadata:
#   - Generic validation:
# 	    . Mandatory STAC extensions in stac_extensions list: eopf, stac base 1.1.0
#       . Verify list of extensions : if one is missing or not used in the properties
#       . Validate against extensions schemas listed
#   - If the schema is available in the CPM install it will use it else it will download it

# * Other metadata:
# 	- Generic validation: No particular restrictions
#   - Template validation: other metadata should respect the template


def is_valid_container(
    container: EOContainer,
    validation_mode: Optional[ValidationMode] = None,
) -> tuple[bool, List[AnomalyDescriptor]]:
    """
    Returns a boolean indicating the validity of the product
    And the list of anomalies

    Parameters
    ----------
        container (EOContainer): input EOContainer
        validation_mode (str): selected validation mode: possible values:
            - STRUCTURE : only verify structure
            - STAC : STAC attr validation
            - MODEL : validate against pydantic model
    Returns
    -------
        Boolean indicating whether a product is valid
        List of anomalies, empty if none found
    """
    logger = EOLogging().get_logger("eopf.container.validation")
    validation_mode = validation_mode if validation_mode is not None else ValidationMode.STRUCTURE
    anomalies: List[AnomalyDescriptor] = []
    checks_to_do: dict[ValidationMode, List[Callable[[Any, List[AnomalyDescriptor], Logger], None]]] = {
        ValidationMode.STRUCTURE: [check_eocontainer_validity],
        ValidationMode.STAC: [check_stac_validity],
        ValidationMode.MODEL: [check_container_model_validity],
        ValidationMode.NONE: [],
    }

    # try:
    for m in ValidationMode:
        if (validation_mode & m) == m:
            for check in checks_to_do[m]:
                check(container, anomalies, logger)
    return len(anomalies) == 0, anomalies


############################################
#   Structure validation part
############################################


def check_eocontainer_validity(container: EOContainer, out_anomalies: List[AnomalyDescriptor], logger: Logger) -> None:
    """
    Check if the input container has a valid format.
    A generic EOContainer validation is applied for all products.
    What's more, if the product type is defined, a product validation based on the templates data structure
    is also applied.

    Parameters
    ----------
        container (EOContainer): input EOContainer
        validation_mode (str): selected validation mode: possible values
    """
    # ----------------- Generic checks
    # Check mandatory attribute categories exist in the EOProduct
    check_attributes_top_category(container, out_anomalies, logger)

    for _, element in container.items():
        if isinstance(element, EOProduct):
            check_eoproduct_validity(element, out_anomalies, logger)
        if isinstance(element, EOContainer):
            check_eocontainer_validity(element, out_anomalies, logger)


############################################
#   EOContainer contract validation part
############################################


class EOContainerModel(BaseModel):
    """
    Pydantic container model
    """

    container_type_regex: str = ".*"
    sub_products: Optional[Dict[str, EOProductModel]] = None
    sub_containers: Optional[Dict[str, "EOContainerModel"]] = None
    attrs: Optional[Dict[str, "AttributeModel"]] = None
    # Will retain a jsonschema
    attrs_schema: Optional[Dict[str, Any]] = None
    required: bool = True


def validate_container_against_model(
    container: EOContainer,
    model: EOContainerModel,
    mode: ModelValidationMode,
    out_anomalies: list[AnomalyDescriptor],
    logger: Logger,
) -> None:
    """
    Validate container against its model

    Parameters
    ----------
    container
    model
    mode
    out_anomalies
    logger

    Returns
    -------

    """
    logger.info(f"Validating {container.name}")
    _validate_container_type(container, model, out_anomalies, logger)
    product_regex_matched, container_regex_matched = _validate_container_elements(
        container,
        model,
        mode,
        out_anomalies,
        logger,
    )
    _validate_mandatory_container_elements(
        container,
        model,
        mode,
        out_anomalies,
        logger,
        container_regex_matched,
        product_regex_matched,
    )
    validate_attrs_against_jsonschema(container, model.attrs_schema, mode, out_anomalies, logger)
    validate_attrs_against_model(container, model.attrs, mode, out_anomalies, logger)


def _validate_mandatory_container_elements(
    container: EOContainer,
    model: EOContainerModel,
    mode: ModelValidationMode,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
    container_regex_matched: list[str],
    product_regex_matched: list[str],
) -> None:
    """
    Validate mandatory elements in a container

    Parameters
    ----------
    container
    model
    mode
    out_anomalies
    logger
    container_regex_matched
    product_regex_matched

    Returns
    -------

    """
    if mode in ("EXACT", "AT_LEAST"):
        if model.sub_products is not None:
            for name_regex, product_model in model.sub_products.items():
                if name_regex not in product_regex_matched and product_model.required:
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Sub-product regex '{name_regex}' not found in container "
                        f"'{container.name}' while required",
                        logger,
                    )
        if model.sub_containers is not None:
            for name_regex, container_model in model.sub_containers.items():
                if name_regex not in container_regex_matched and container_model.required:
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Sub-container regex '{name_regex}' not found in container '{container.name}' while required",
                        logger,
                    )


def _validate_container_elements(
    container: EOContainer,
    model: EOContainerModel,
    mode: ModelValidationMode,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
) -> Tuple[list[str], list[str]]:
    """
    Validate sub element of container

    Parameters
    ----------
    container
    model
    mode
    out_anomalies
    logger

    Returns
    -------

    """
    product_regex_matched: list[str] = []
    container_regex_matched: list[str] = []
    for name, element in container.items():
        if isinstance(element, EOProduct):
            if not _validate_sub_product(element, model, mode, out_anomalies, logger, name, product_regex_matched):
                if mode == "EXACT":
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Product '{name}' not matched in model but is in {container.name}",
                        logger,
                    )
        else:
            if not _validate_sub_container(element, model, mode, out_anomalies, logger, name, container_regex_matched):
                if mode == "EXACT":
                    append_to_anomalies(
                        out_anomalies,
                        "MODEL",
                        f"Sub-container '{name}' not matched in model but is in {container.name}",
                        logger,
                    )
    return product_regex_matched, container_regex_matched


def _validate_sub_container(
    container: EOContainer,
    model: EOContainerModel,
    mode: ModelValidationMode,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
    name: str,
    container_regex_matched: list[str],
) -> bool:
    """
    Validate sub containers of the container

    Parameters
    ----------
    container
    model
    mode
    out_anomalies
    logger
    name
    container_regex_matched

    Returns
    -------

    """
    logger.info(f"Validating sub container {container.name}")
    found = False
    if model.sub_containers is not None:
        for name_regex, container_model in model.sub_containers.items():
            if re.fullmatch(name_regex, name):
                found = True
                container_regex_matched.append(name_regex)
                validate_container_against_model(container, container_model, mode, out_anomalies, logger)
    return found


def _validate_sub_product(
    product: EOProduct,
    model: EOContainerModel,
    mode: ModelValidationMode,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
    name: str,
    product_regex_matched: list[str],
) -> bool:
    """
    Validate sub product of the container

    Parameters
    ----------
    product
    model
    mode
    out_anomalies
    logger
    name
    product_regex_matched

    Returns
    -------

    """
    logger.info(f"Validating sub product {product.name}")
    found = False
    if model.sub_products is not None:
        for name_regex, product_model in model.sub_products.items():
            if re.fullmatch(name_regex, name):
                found = True
                product_regex_matched.append(name_regex)
                validate_product_against_model(product, product_model, mode, out_anomalies, logger)
    return found


def _validate_container_type(
    container: EOContainer,
    model: EOContainerModel,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
) -> None:
    """
    Validate the container type according to the model

    Parameters
    ----------
    container
    model
    out_anomalies
    logger

    Returns
    -------

    """
    if model.container_type_regex == ".*":
        return
    if container.container_type is None:
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            "Input container type is None",
            logger,
        )
    elif not re.fullmatch(model.container_type_regex, container.container_type):
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            f"Wrong container type detected on product '{container.container_type}' "
            f"doesn't match '{model.container_type_regex}'",
            logger,
        )


def check_container_model_validity(
    container: EOContainer,
    out_anomalies: List[AnomalyDescriptor],
    logger: Logger,
    check_submodels: bool = True,
) -> None:
    """
    Check if the input product/container is valid against it's model.
    .

    Parameters
    ----------
        logger
        out_anomalies
        check_submodels : check sub products and sub containers against their own models
        container: input EOContainer

    """

    models_folder = EOConfiguration().get("model__folder")
    if container.container_type is None:
        append_to_anomalies(out_anomalies, "MODEL", f"No container type found in container '{container.name}'", logger)
        return
    model_local = AnyPath.cast(models_folder) / f"{container.container_type}.json"
    if not model_local.exists():
        append_to_anomalies(
            out_anomalies,
            "MODEL",
            f"No container type model '{model_local.path}' found in folder '{models_folder}'",
            logger,
        )
        return
    data = load_json_file(model_local)
    loaded_cont = EOContainerModel(**data)
    validate_container_against_model(container, loaded_cont, "EXACT", out_anomalies, logger)

    if check_submodels:
        for element in container.values():
            if isinstance(element, EOContainer):
                check_container_model_validity(element, out_anomalies, logger, check_submodels)
            elif isinstance(element, EOProduct):
                check_product_model_validity(element, out_anomalies, logger)


################################################
# EOContainer Model utility functions
################################################


def container_to_model(container: EOContainer) -> EOContainerModel:
    """
    Get the pydantic model out of the container
    might need some manual modifications

    Parameters
    ----------
    container

    Returns
    -------

    """
    return EOContainerModel(
        container_type_regex=container.container_type if container.container_type is not None else ".*",
        attrs={p: AttributeModel() for p in get_all_paths_in_dict(container.attrs)},
        sub_products={n: product_to_model(product=p) for n, p in container.items() if isinstance(p, EOProduct)},
        sub_containers={n: container_to_model(container=c) for n, c in container.items() if isinstance(c, EOContainer)},
    )


def container_to_model_json_file(container: EOContainer, filepath: AnyPath) -> None:
    """
    Create pydantic json model file from the container

    Parameters
    ----------
    container
    filepath

    Returns
    -------

    """
    with filepath.open("w") as f:
        f.write(container_to_model(container).model_dump_json(indent=4, exclude_unset=True))


def model_to_container(model: EOContainerModel) -> EOContainer:
    """
    Create a dummy container from a model

    Parameters
    ----------
    model

    Returns
    -------

    """
    attrs_to_use = {} if model.attrs is None else model.attrs
    result = EOContainer(
        name="TOBEDEFINED",
        attrs=nested_dict_from_paths(list(attrs_to_use.keys())),
        type=model.container_type_regex,
    )
    if model.sub_products is not None:
        for product_name, constraint in model.sub_products.items():
            result[product_name] = model_to_product(constraint)
    if model.sub_containers is not None:
        for container_name, container_constraint in model.sub_containers.items():
            result[container_name] = model_to_container(container_constraint)

    return result


def check_coherent_dimension_container(
    eo_container: EOContainer,
    out_anomalies: List[AnomalyDescriptor],
    logger: Optional[Logger],
) -> None:
    """
    Chack that the dimensions of the container are coherent together

    Parameters
    ----------
    eo_container
    out_anomalies
    logger

    Returns
    -------

    """
    for p in eo_container.values():
        if isinstance(p, EOProduct):
            check_coherent_dimension_product(p, out_anomalies, logger)
        else:
            check_coherent_dimension_container(p, out_anomalies, logger)
