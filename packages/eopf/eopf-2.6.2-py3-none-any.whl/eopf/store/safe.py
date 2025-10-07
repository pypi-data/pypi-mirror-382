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
safe.py

EOSafeStore implementation

"""
import importlib
import os
from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from re import match
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from eopf import EOLogging, OpeningMode
from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.accessor.abstract import AccessorStatus
from eopf.common.constants import (
    EOCONTAINER_CATEGORY,
    EOPF_CATEGORY_ATTR,
    EOPRODUCT_CATEGORY,
    EOV_IS_MASKED,
    EOV_IS_SCALED,
    NO_PATH_MATCH,
)
from eopf.common.file_utils import AnyPath

# Warning : do not remove this is the factory registry mechanism
from eopf.config import EOConfiguration
from eopf.exceptions.errors import (
    AccessorInitError,
    AccessorOpenError,
    AccessorRetrieveError,
    EOStoreInvalidRequestError,
    EOVariableAssignCoordsError,
    MappingDefinitionError,
    MappingMissingError,
    StoreInvalidMode,
    StoreLoadFailure,
    StoreMissingAttr,
    StoreOpenFailure,
    StoreReadFailure,
)
from eopf.exceptions.warnings import EOSafeStoreWarning, MappingMissingDimensionsWarning
from eopf.product import EOContainer, EOGroup, EOProduct, EOVariable
from eopf.product.eo_object import EOObject
from eopf.product.utils.eoobj_utils import NONE_EOObj, is_None_EOObj
from eopf.product.utils.transformers_utils import (
    transformation_astype,
    transformation_attributes,
    transformation_dimensions,
    transformation_dopplerTime,
    transformation_expand_dims,
    transformation_mask_and_scale,
    transformation_pack_bits,
    transformation_rechunk,
    transformation_scale,
    transformation_squeeze,
    transformation_sub_array,
    transformation_transpose,
)
from eopf.store.abstract import EOProductStore
from eopf.store.mapping_manager import EOPFAbstractMappingManager, EOPFMappingManager
from eopf.store.store_factory import EOStoreFactory

TARGET_PATH_SEPARATOR = ":"
EO_PATH_SEPARATOR = "/"
COORDS_TAG = f"coords{TARGET_PATH_SEPARATOR}"
ATTRS_TAG = "attrs:"
COORDS_WITH_NAMESPACE_PATTERN = rf"^{COORDS_TAG}(\w+){TARGET_PATH_SEPARATOR}(\w+)$"
COORDS_WITHOUT_NAMESPACE_PATTERN = rf"^{COORDS_TAG}(\w+)$"
DEFAULT_COORDS_NAMESPACE = "global"
EO_OBJ_DESCRIPTION_COORDS_NAMESPACE = "coords_namespace"
ATTRS_TARGET_PATH_PATTERN = rf"^{ATTRS_TAG}([\w/]+){TARGET_PATH_SEPARATOR}([\w+\./]+)$"
DEFAULT_ATTRS_TARGET = "/"
ATTRS_DICT_TOP_LEVEL_IDENTIFIER = "/"
DICT_PATH_DELIMITER = "/"


class EOSafeInit(ABC):
    """
    Init class abstract to fill the init_function section in the mappings

    .. code-block:: JSON
      :emphasize-lines: 6,7,8

        {
                "recognition": {
                    "filename_pattern": "test_product.SEN3",
                    "product_type": "new_product_type"
                },
                "init_function": {
                    "module" : "tests.store.fake_init_function",
                    "class" : "default_init_function"
                },
                "finalize_function": {
                    "module" : "tests.store.fake_init_function",
                    "function" : "default_finalize_function"
                },
                "data_mapping": [
                    ]
        }

    """

    @abstractmethod
    def init_product(
        self,
        url: AnyPath,
        name: str,
        attrs: Dict[str, Any],
        product_type: str,
        processing_version: str,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> EOProduct:
        """

        Parameters
        ----------
        url : AnyPath, path to the product on disc
        name : name of the product
        attrs : attribute dict loaded from the attr section in the mapping
        product_type : product type
        processing_version : processing version
        mapping : Optional[dict[str, Any]] origin mapping
        mapping_manager : EOPFMappingManager
        eop_kwargs : other kwargs passed to the load call in eop_kwargs

        Returns
        -------
        An EOProduct
        """

    @abstractmethod
    def init_container(
        self,
        url: AnyPath,
        name: str,
        attrs: Dict[str, Any],
        product_type: str,
        processing_version: str,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> EOContainer:
        """

        Parameters
        ----------
        url : AnyPath, path to the product on disc
        name : name of the product
        attrs : attribute dict loaded from the attr section in the mapping
        product_type : product type
        processing_version : processing version
        mapping : Optional[dict[str, Any]] origin mapping
        mapping_manager : EOPFMappingManager
        eop_kwargs : other kwargs passed to the load call in eop_kwargs

        Returns
        -------
        An EOContainer
        """


class EOSafeFinalize(ABC):
    """
    Finalize class abstract to fill the finalize_function section in the mappings

    .. code-block:: JSON
      :emphasize-lines: 10,11,12

        {
                "recognition": {
                    "filename_pattern": "test_product.SEN3",
                    "product_type": "new_product_type"
                },
                "init_function": {
                    "module" : "tests.store.fake_init_function",
                    "class" : "default_init_function"
                },
                "finalize_function": {
                    "module" : "tests.store.fake_init_function",
                    "function" : "default_finalize_function"
                },
                "data_mapping": [
                    [
        }

    """

    @abstractmethod
    def finalize_product(
        self,
        eop: EOProduct,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        """

        Parameters
        ----------
        eop: EOProduct input eoproduct to finalize
        url : AnyPath, path to the product on disc
        mapping : Optional[dict[str, Any]] origin mapping
        mapping_manager : EOPFMappingManager
        eop_kwargs : other kwargs passed to the load call in eop_kwargs

        Returns
        -------
        None
        """

    @abstractmethod
    def finalize_container(
        self,
        container: EOContainer,
        url: AnyPath,
        mapping: Optional[dict[str, Any]],
        mapping_manager: EOPFAbstractMappingManager,
        **eop_kwargs: Any,
    ) -> None:
        """

        Parameters
        ----------
        container: EOContainer input EOContainer to finalize
        url : AnyPath, path to the product on disc
        mapping : Optional[dict[str, Any]] origin mapping
        mapping_manager : EOPFMappingManager
        eop_kwargs : other kwargs passed to the load call in eop_kwargs

        Returns
        -------
        An EOContainer
        """


@EOStoreFactory.register_store("safe")
class EOSafeStore(EOProductStore):
    """
    EOSafeStore implementation
    """

    EXTENSION = ".SAFE"
    DEFAULT_TRANSFORMERS_LIST: list[tuple[str, Callable[[EOObject, Any], EOObject]]] = [
        ("doppler_time", transformation_dopplerTime),
        ("attributes", transformation_attributes),
        ("mask_and_scale", transformation_mask_and_scale),
        ("astype", transformation_astype),
        ("sub_array", transformation_sub_array),
        ("pack_bits", transformation_pack_bits),
        ("transpose", transformation_transpose),
        ("squeeze", transformation_squeeze),
        ("scale", transformation_scale),
        (
            "dimensions",
            transformation_dimensions,
        ),  # dimensions should be after dimension dependant tranfo
        (
            "rechunk",
            transformation_rechunk,
        ),  # rechunk should be after dimensions since it matches on the new dimensions
    ]
    DEFAULT_REVERSE_TRANSFORMERS_LIST: list[tuple[str, Callable[["EOObject", Any], "EOObject"]]] = [
        ("transpose", transformation_transpose),
        ("expand_dims", transformation_expand_dims),
        (
            "dimensions",
            transformation_dimensions,
        ),  # dimensions should be after dimension dependant tranfo
    ]

    def __init__(
        self,
        url: str | AnyPath,
        *args: Any,
        mapping_manager: Optional[EOPFAbstractMappingManager] = None,
        mask_and_scale: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initializes the EOSafeStore

        Parameters
        ----------
        url: str|AnyPath
            file system path to a product
        mapping_manager: EOPFAbstractMappingManager,
            mapping manager to be used upon mappings
        mask_and_scale: Optional[bool] = None
            apply or not masking and scaling by overriding EOConfiguration
        args:
            None
        kwargs:
            storage_options: dict[Any, Any] parameters for AnyPath

        Raises
        -------

        Returns
        -------
        """
        super().__init__(url, *args, **kwargs)
        self._original_url: Optional[AnyPath] = None
        self._accessor_factory = EOAccessorFactory()
        self._logger = EOLogging().get_logger("eopf.store.safe")
        self._mapping_manager: EOPFAbstractMappingManager = (
            mapping_manager if mapping_manager is not None else EOPFMappingManager()
        )
        self._mapping: Optional[dict[str, Any]] = None
        self._is_loaded: bool = False
        self._attrs_map: dict[str, dict[str, Any]] = {}
        self._data_map: dict[str, Any] = {}
        self._coords_dict: dict[str, list[Any]] = {DEFAULT_COORDS_NAMESPACE: []}
        self._root: Optional[Union[EOProduct, EOContainer]] = None
        self._eov_kwargs: dict[str, Any] = {}
        self._accessors_cache: dict[int, EOAccessor] = {}
        self._accessors_data_cache: dict[int, EOObject] = {}
        self._eo_init_function: Optional[EOSafeInit] = None
        self._eo_finalize_function: Optional[EOSafeFinalize] = None
        if mask_and_scale is None:
            eopf_config = EOConfiguration()
            self._mask_and_scale = eopf_config.get("product__mask_and_scale")
        else:
            self._mask_and_scale = mask_and_scale

    def _is_coord(self, eov_dims: tuple[str, ...], coord_dims: list[str]) -> bool:
        """
        Determine if the current coordinate, give by coord_dims, is a coordinate for an EOVariable, given by eov_dims

        Parameters
        ----------
        eov_dims: list[str]
            list of EOVariable dimensions
        coord_dims: list[str]
            list of coordinate dimensions

        Raises
        -------

        Returns
        -------
        bool
        """
        for coord_dim in coord_dims:
            if coord_dim not in eov_dims:
                return False

        return True

    def _eov_assign_coords(self, eov: EOVariable, namespace: str) -> EOVariable:
        """
        Assign coordinate to the given EOVariable by searching in the coords_dict

        Parameters
        ----------
        eov: EOVariable
            given EOVariable
        namespace: str
            coordinates namespace

        Raises
        -------
        EOVariableAssignCoordsError
        MappingDefinitionError

        Returns
        -------
        EOVariable
        """

        if namespace not in self._coords_dict:
            raise MappingDefinitionError(f"Coordinates namespace: {namespace} was not defined")

        try:
            # If any coord dims is not available return original eov
            if self.__has_missing_coord_description(namespace):
                return eov

            # Extract the corresponding coords for the namespace
            coords_attrs, coords_dict = self.__eov_extract_coords(eov, namespace)

            # warn if no coordinate is assigned, probably the mapping as been defined wrong
            # pytest patches logging for better test output and stricter argument handling
            # -> doesn't accept second parameter as message
            if len(coords_dict) == 0:
                self._logger.debug(
                    f"EOVariable with attrs:{eov.attrs}; has no coordinate assigned."
                    f"{MappingMissingDimensionsWarning.__name__}: {MappingMissingDimensionsWarning.__doc__}",
                )
                return eov

            data_with_coord = eov.data.assign_coords(coords_dict)
            # update coordinates attributes when empty - temporary fix for issue #543
            for coord_name, _ in data_with_coord.coords.items():
                if not data_with_coord[coord_name].attrs:
                    for key in coords_attrs[coord_name]:
                        if key == "dimensions":
                            data_with_coord[coord_name].attrs[key] = list(coords_attrs[coord_name][key])
                        else:
                            data_with_coord[coord_name].attrs[key] = coords_attrs[coord_name][key]

        except Exception as err:
            raise EOVariableAssignCoordsError(
                f'Can not assign {coords_dict} to {eov.attrs["long_name"]}: {err}',
            ) from err

        ret_eov = eov._init_similar(data_with_coord)
        # Update the eov attr based on this coords update
        self.__eov_update_attrs_coords(ret_eov)

        return ret_eov

    def __has_missing_coord_description(self, namespace: str) -> bool:
        """
        Detect if there is a missing dims definition in the coords description for the required namespace

        Parameters
        ----------
        namespace : namespace to look into

        Returns
        -------
        bool : true if has a missing dims

        """
        has_missing_coords = any(
            coord_dims is None
            for coord_dims in (
                self._resolve_coord_dims(coord_description) for coord_description in self._coords_dict[namespace]
            )
        )
        return has_missing_coords

    def __eov_extract_coords(self, eov: EOVariable, namespace: str) -> Tuple[dict[Any, Any], dict[Any, Any]]:
        coords_dict = {}
        coords_attrs: dict[Any, Any] = {}
        for coord_description in self._coords_dict[namespace]:
            coord_dims = self._resolve_coord_dims(coord_description)
            if self._is_coord(eov.dims, coord_dims):
                eov_coord_name = self.__resolve_eov_coord_name(coord_description)
                coord = self._get_eo_obj(coord_description)
                if coord is not NONE_EOObj and isinstance(coord, EOVariable):
                    coords_dict[eov_coord_name] = (coord_dims, coord.data.data)
                    coords_attrs[eov_coord_name] = coord.attrs
        return coords_attrs, coords_dict

    @staticmethod
    def __eov_update_attrs_coords(eov: EOVariable) -> None:

        for coord_name in eov.coords:
            if EOV_IS_SCALED in eov.coords[coord_name].attrs and eov.coords[coord_name].attrs[EOV_IS_SCALED] is True:
                eov.attrs[EOV_IS_SCALED] = True
            if EOV_IS_MASKED in eov.coords[coord_name].attrs and eov.coords[coord_name].attrs[EOV_IS_MASKED] is True:
                eov.attrs[EOV_IS_MASKED] = True

    @staticmethod
    def __resolve_eov_coord_name(coord_description: Any) -> str:
        """
        Resolve the coord name by removing namespace
        Parameters
        ----------
        coord_description

        Returns
        -------

        """
        target_path = coord_description["target_path"]
        coord_with_namespace = match(COORDS_WITH_NAMESPACE_PATTERN, target_path)
        coord_without_namespace = match(COORDS_WITHOUT_NAMESPACE_PATTERN, target_path)
        if coord_with_namespace is not None:
            coord_name = coord_with_namespace[2]
        elif coord_without_namespace is not None:
            coord_name = coord_without_namespace[1]
        else:
            raise MappingDefinitionError(
                f"coordinates' target_path: {target_path};"
                f" need to match: {COORDS_WITH_NAMESPACE_PATTERN} "
                f"or {COORDS_WITHOUT_NAMESPACE_PATTERN}",  # noqa: E501
            )
        return coord_name

    def _resolve_coord_dims(self, coord_description: Any) -> Any:
        """
        Resolve the coordinate dimension name
        Parameters
        ----------
        coord_description

        Returns
        -------

        """
        if "attributes" in coord_description and "dimensions" in coord_description["attributes"]:
            # TBD, harmonization, attributes should be under transform not directly under the eo_obj_description
            return coord_description["attributes"]["dimensions"].split(" ")
        if "attributes" in coord_description and "dimensions" in coord_description["transform"]["attributes"]:
            return coord_description["transform"]["attributes"]["dimensions"].split(" ")
        if "dimensions" in coord_description["transform"]:
            if "eopf" in coord_description["transform"]["dimensions"]:
                # when both the eopf and legacy safe dimensions are specified
                return coord_description["transform"]["dimensions"]["eopf"]
            return coord_description["transform"]["dimensions"]
        self._logger.warning(
            f'{coord_description["source_path"]} is missing dimensions.'
            f"{MappingMissingDimensionsWarning.__name__}: {MappingMissingDimensionsWarning.__doc__}",
        )
        return None

    def _apply_transformers(self, eo_obj_description: Dict[str, Any], eo_obj: EOObject) -> "EOObject":
        """
        Apply transformers to the EOVariables read by the accessors

        Parameters
        ----------
        eo_obj_description: Dict[str, Any])
            EOObject description from the mapping

        Raises
        -------
        EOStoreInvalidRequestError

        Returns
        -------
        EOObject
        """
        if "transform" not in eo_obj_description:
            return eo_obj

        for transformer_name, transformer_parameters in self.DEFAULT_TRANSFORMERS_LIST:
            try:
                if transformer_name in eo_obj_description["transform"]:
                    if (
                        isinstance(eo_obj_description["transform"][transformer_name], dict)
                        and "eopf" in eo_obj_description["transform"][transformer_name]
                    ):
                        transformation_parameters = eo_obj_description["transform"][transformer_name]["eopf"]
                    else:
                        transformation_parameters = eo_obj_description["transform"][transformer_name]
                    # Safe store needs to be able to override EOConfiguration mask and scale
                    # hence we pass the parameter specifically to this transformer as it is
                    # also responsible of masking and scaling
                    if transformer_name == "mask_and_scale":
                        transformation_parameters["mask_and_scale"] = self._mask_and_scale
                    eo_obj = transformer_parameters(eo_obj, transformation_parameters)

            except Exception as err:
                raise EOStoreInvalidRequestError(
                    f"Applying parameter {transformer_name} on {eo_obj_description} failed due to {err}",
                ) from err

        return eo_obj

    def close_accessors(self) -> None:
        """
        Closes all open accessors in the accessors cache.

        This method iterates through all accessors in the accessors cache
        and closes any accessor that is currently in an open status.

        Returns:
            None
        """
        for _, accessor in self._accessors_cache.items():
            if accessor.status is AccessorStatus.OPEN:
                accessor.close()
        self._accessors_cache = {}
        self._accessors_data_cache = {}

    def _parse_eo_obj_description_for_legacy_attributes(
        self,
        eo_obj_description: dict[str, Any],
        eo_obj_attrs: dict[str, Any],
        file_path: str = "",
        var_path: str = "",
    ) -> dict[str, Any]:
        """
        Parses and eo_obj_description and replaces values marked as <from_legacy:legacy_attr_name>
        with the value of the attr from legacy retrieve eo_obj.attrs
        """

        for k, v in eo_obj_description.items():
            if isinstance(v, dict):
                # parse sub dictionaries
                eo_obj_description[k] = self._parse_eo_obj_description_for_legacy_attributes(
                    v,
                    eo_obj_attrs,
                    file_path=file_path,
                    var_path=var_path,
                )
            elif isinstance(v, str):
                legacy_match = match("^from_legacy_attr:(.*)$", v)
                if legacy_match is not None:
                    legacy_attribute_name = legacy_match[1]
                    if legacy_attribute_name in eo_obj_attrs:
                        eo_obj_description[k] = eo_obj_attrs[legacy_attribute_name]
                    else:
                        raise StoreLoadFailure(
                            f"{file_path}:{var_path}: Legacy attribute {legacy_attribute_name} can not be found!",
                        )
                else:
                    pass
            else:
                pass

        return eo_obj_description

    def _get_eo_obj(self, eo_obj_description: Dict[str, Any]) -> "EOObject":
        """
        Retrieve an EOObject based on mapping description of the EObject

        Parameters
        ----------
        eo_obj_description: Dict[str, Any])
            EOObject description from the mapping

        Raises
        -------
        MappingAccessorNotFoundError
        AccessorOpenError
        AccessorRetrieveError

        Returns
        -------
        "EOObject"
        """

        # retrieve file_path and var_path from mapping source_path
        # the source_path has the format file_path:var_path
        file_path, product_file_path, var_path = self.__resolve_product_file_path(eo_obj_description)

        # Is this data optional in the mapping ?
        is_optional = eo_obj_description.get("is_optional")

        if file_path == NO_PATH_MATCH:
            if is_optional:
                return NONE_EOObj
            raise FileNotFoundError(f"No file was found under {self.url} for eo_obj: {eo_obj_description}")

        # retrieve accessor configurations as kwargs
        # the safe store is not aware of the logic of the accessor
        # hence it will pass the accessor kwargs both to the init and open functions
        # the accessor implementation should extract the proper arguments
        accessor_config: dict[str, Any] = {}
        if "accessor_config" in eo_obj_description:
            accessor_config = eo_obj_description["accessor_config"]
        # Get the accessor
        try:
            accessor, dynamic_params, _ = self.__get_accessor(
                accessor_config,
                eo_obj_description["accessor_id"],
                product_file_path,
            )
        except AccessorInitError:
            raise
        except Exception as err:
            # optional eo_obj should not be reported as missing
            if is_optional:
                return NONE_EOObj
            raise AccessorOpenError(f"{err}") from err

        # retrieve data via accessor get_data
        try:
            eo_obj = self.__get_eo_obj_data(accessor, dynamic_params, eo_obj_description, file_path, var_path)
        except (FileNotFoundError, KeyError, AccessorRetrieveError) as err:
            # optional eo_obj should not be reported as missing
            if is_optional:
                return NONE_EOObj
            else:
                raise AccessorRetrieveError(f"{err}") from err

        # apply transformers in necessary or return the object as read by the accessor
        return self._apply_transformers(eo_obj_description, eo_obj)

    def __resolve_product_file_path(self, eo_obj_description: Dict[str, Any]) -> Tuple[str, AnyPath, str]:
        PATH_DELIMITER = ":"
        if "local_path" in eo_obj_description:
            file_path = eo_obj_description["source_path"]
            var_path = eo_obj_description["local_path"]
        elif PATH_DELIMITER in eo_obj_description["source_path"]:
            file_path, var_path = eo_obj_description["source_path"].split(PATH_DELIMITER)
        else:
            file_path = eo_obj_description["source_path"]
            var_path = ""
        product_file_path: AnyPath = self.url / file_path
        return file_path, product_file_path, var_path

    def __get_accessor(
        self,
        accessor_config: Dict[str, Any],
        accessor_id: str,
        product_file_path: AnyPath,
    ) -> Tuple[EOAccessor, Dict[str, Any], bool]:
        """
        Get the accessor and the corresponding dynamic config
        Parameters
        ----------
        accessor_config
        accessor_id
        product_file_path

        Returns
        -------

        """
        # determine the accessor to be used
        accessor_class = self._accessor_factory.get_accessor_class(
            file_path=product_file_path.path,
            accessor_id=accessor_id,
        )
        # init the accessor
        accessor_config, dynamic_params = accessor_class.trim_params(accessor_config)
        accessor_key = hash(str(product_file_path) + str(accessor_class) + str(sorted(accessor_config.items())))
        if accessor_key not in self._accessors_cache:
            try:
                accessor = accessor_class(product_file_path, **accessor_config)
            except Exception as err:
                raise AccessorInitError(f"{err}") from err
            accessor.open(**{**accessor_config, **dynamic_params})
            self._accessors_cache[accessor_key] = accessor
            return accessor, dynamic_params, False
        else:
            accessor = self._accessors_cache[accessor_key]
            return accessor, dynamic_params, True

    def __get_eo_obj_data(
        self,
        accessor: EOAccessor,
        dynamic_params: dict[str, Any],
        eo_obj_description: dict[str, Any],
        file_path: str,
        var_path: Any,
    ) -> EOObject:
        """
        Extract the data from the accessor and apply post modification
        Parameters
        ----------
        accessor
        dynamic_params : parameters for accessor that need to be given for each data extraction.
                        See EOAccessor.trim_params
        eo_obj_description
        file_path
        var_path

        Returns
        -------

        """
        data_key = hash(
            str(accessor.__class__)
            + str(dynamic_params.items())
            + str(eo_obj_description.items())
            + str(file_path)
            + str(var_path),
        )
        if data_key in self._accessors_data_cache:
            return self._accessors_data_cache[data_key]

        eo_obj: EOObject = accessor.get_data(var_path, **dynamic_params)
        # remove attrs from accessor not retrieving attrs data
        if not eo_obj_description["target_path"].startswith("attrs:"):
            self._parse_eo_obj_description_for_legacy_attributes(
                eo_obj_description,
                eo_obj_attrs=eo_obj.attrs,
                file_path=file_path,
                var_path=var_path,
            )
            eo_obj.attrs = {}
        # remove legacy coords from data
        if isinstance(eo_obj, EOVariable):
            if len(eo_obj.coords) > 0:
                # we should drop all coordinates, however as reported
                # in issue 555 drop does not really drop legacy coords
                eo_obj = EOVariable("", data=eo_obj.data.data)
        self._accessors_data_cache[data_key] = eo_obj
        return eo_obj

    def __getitem__(self, key: str) -> "EOObject":
        """
        Retrieve an EOObject based on mapping description of the EObject

        Parameters
        ----------
        key: str

        Raises
        -------
        MappingAccessorNotFoundError
        AccessorOpenError
        AccessorRetrieveError

        Returns
        -------
        Optional["EOObject"]
        """

        self.check_is_opened()

        if key.startswith(ATTRS_TAG):
            return EOGroup(attrs=self._get_attrs_tag_item(key))

        if key.endswith("/"):
            self._logger.warning(
                f"EOSafeStore does not support EOGroup get."
                f"{EOSafeStoreWarning.__name__}: {EOSafeStoreWarning.__doc__}",
            )
            return NONE_EOObj

        if key not in self._data_map:
            self._logger.warning(
                f"{key} does not exist. {EOSafeStoreWarning.__name__}: {EOSafeStoreWarning.__doc__}",
            )
            return NONE_EOObj

        eo_obj_description = self._data_map[key]

        # retrieve short name from mapping and put it into transformation attributes
        if "short_name" in eo_obj_description:
            transform = eo_obj_description.setdefault("transform", {})
            attributes = transform.setdefault("attributes", {})
            attributes["short_name"] = eo_obj_description.get("short_name")

        # retrieve eo_obj based on its description
        eo_obj = self._get_eo_obj(eo_obj_description)

        # retrieve coords namespace
        if EO_OBJ_DESCRIPTION_COORDS_NAMESPACE in eo_obj_description:
            coords_namespace = eo_obj_description[EO_OBJ_DESCRIPTION_COORDS_NAMESPACE]
        else:
            coords_namespace = DEFAULT_COORDS_NAMESPACE

        if eo_obj is None:
            return NONE_EOObj

        if isinstance(eo_obj, EOVariable):
            if len(eo_obj.dims) == 0:
                self._logger.debug(
                    f"EOVariable with description:{eo_obj_description}; is missing dimensions",
                )
                return eo_obj
            return self._eov_assign_coords(eo_obj, coords_namespace)
        return eo_obj

    def _get_attrs_tag_item(self, key: str) -> dict[str, Any]:
        """
        Get an attribute only item

        Parameters
        ----------
        key

        Returns
        -------

        """
        # Resolve the paths of the target attrs
        dict_path, eo_path = self.__resolve_attrs_paths(key)
        # retrieve all necessary eo_obj descriptions
        list_eo_obj_description: list[Any] = []
        if dict_path == ATTRS_DICT_TOP_LEVEL_IDENTIFIER:
            # in case we want all attrs related that be retrieved from the specified eo_path
            for k in self._attrs_map[eo_path]:
                list_eo_obj_description.extend(self._attrs_map[eo_path][k])
        else:
            list_eo_obj_description.extend(self._attrs_map[eo_path][dict_path])
        attrs: dict[str, Any] = {}
        for eo_obj_description in list_eo_obj_description:
            dict_path = eo_obj_description["target_path"].split(TARGET_PATH_SEPARATOR)[2]
            if dict_path == ATTRS_DICT_TOP_LEVEL_IDENTIFIER:
                cur_attrs = self._get_eo_obj(eo_obj_description).attrs
                _ = self._merge_dict_attrs(attrs, cur_attrs)
                continue
            cur_attrs = {}
            dict_path_keys = dict_path.split(DICT_PATH_DELIMITER)
            reference = cur_attrs
            for k in dict_path_keys:
                if k == "":
                    continue
                reference.setdefault(k, {})
                reference = reference[k]

            eo_obj = self._get_eo_obj(eo_obj_description)
            for k in eo_obj.attrs:
                reference[k] = eo_obj.attrs[k]
            _ = self._merge_dict_attrs(attrs, cur_attrs)
        return attrs

    def __resolve_attrs_paths(self, key: str) -> Tuple[str, str]:
        """
        Resolve the path of the attrs in the eov

        Parameters
        ----------
        key

        Returns
        -------
        path in the dict, path in the eov
        """
        attrs_pattern_match = match(ATTRS_TARGET_PATH_PATTERN, key)
        if attrs_pattern_match is None:
            raise MappingDefinitionError(
                f"attributes' target_path: {key}; need to match: {ATTRS_TARGET_PATH_PATTERN}",  # noqa: E501
            )
        eo_path = attrs_pattern_match[1]
        dict_path = attrs_pattern_match[2]
        # check existence of the eo_path and dictionary path in the mapping
        if eo_path not in self._attrs_map:
            raise KeyError(
                f"attributes' eo_path: {eo_path}; is not defined in the mapping",  # noqa: E501
            )
        if dict_path not in self._attrs_map[eo_path] and dict_path != DEFAULT_ATTRS_TARGET:
            raise KeyError(
                f"attributes' dict_path: {dict_path}; is not defined in the mapping",  # noqa: E501
            )
        return dict_path, eo_path

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        **kwargs: Any,
    ) -> "EOProductStore":
        """
        Creates any internal dictionaries needed depending on the mode

        Parameters
        ----------
        mode: OpeningMode | str
            opening mode of the store, default to open
        mapping_manager: Optional[type[EOPFAbstractMappingManager]]
            manager used to acquire mapping
        kwargs:
            eov_kwargs: EOVariable init kwargs

        Raises
        -------
        MappingMissingError
        StoreInvalidMode

        Returns
        -------
        EOProductStore
        """
        super().open(mode=mode, **kwargs)
        if self._mode == OpeningMode.OPEN:
            if not self.url.exists():
                raise FileNotFoundError("{self.url} does not exist")

            if not self.guess_can_read(self.url):
                raise StoreReadFailure(f"EOSafeStore can not read product at: {self.url}")

            # in order read the product we need the mapping
            self._mapping, _ = self._mapping_manager.parse_mapping(self.url)

            if self._mapping is None:
                raise MappingMissingError(f"No mapping found for url : {self.url}")

            # get EOVariable kwargs
            if "eov_kwargs" in kwargs:
                self._eov_kwargs = kwargs.pop("eov_kwargs", {})

            try:
                # handle special cases where you need to do additional stuff such as s3 files handling etc
                self._handle_special_cases(mode)

                # Extract internal data structures
                if self._mapping is not None:
                    for eo_obj_description in self._mapping["data_mapping"]:
                        self._extract_internal_data_structure(eo_obj_description)
                # detect external accessor to load
                self._detect_external_accessors()
                # Detect init and finalize functions
                self._detect_init_function()
                self._detect_finalize_function()

            except Exception as err:
                raise StoreOpenFailure(f"{err}") from err

        else:
            raise StoreInvalidMode(f"EOSafeStore does not support mode: {self._mode}")

        return self

    def _handle_special_cases(self, mode: OpeningMode | str = OpeningMode.OPEN) -> None:
        """
        Handles special opening cases
        Returns
        -------

        """

        # S02 products are known not to be able to run from S3 filesystem
        s02_pattern = r".*S2[A-D]_MSI.*"
        if mode == OpeningMode.OPEN and match(s02_pattern, self.url.path):
            # not all accessors are able to read from s3 storage, i.e., s02 rasterio
            # thus we download the product in a local tmp
            if not self.url.islocal():
                self._original_url = (
                    self.url
                )  # The tmp_dir is kept by this instance, is deleted then garbage collected ...
                self._url = AnyPath.cast(self.url.get(recursive=True))

    def _detect_init_function(self) -> None:
        # detect eo init function
        if self._mapping is not None and "init_function" in self._mapping:
            module_name: str = self._mapping["init_function"]["module"]
            # python function to import from the module
            class_name: str = self._mapping["init_function"]["class"]
            try:
                module = importlib.import_module(module_name)
                try:
                    init_class = getattr(module, class_name)
                except AttributeError as exc:
                    raise StoreOpenFailure(
                        f"Class {class_name} not found in module {module_name} for init function",
                    ) from exc
            except (
                ImportError,
                ModuleNotFoundError,
                SyntaxError,
                AttributeError,
                PermissionError,
                ValueError,
                TypeError,
                OSError,
                NameError,
            ) as e:
                raise StoreOpenFailure(f"Error while importing module {module_name} : {type(e)} {e}") from e
            if not issubclass(init_class, EOSafeInit):
                raise StoreOpenFailure(f"{init_class} is not implementing EOSafeInit")

            self._eo_init_function = init_class()

    def _detect_finalize_function(self) -> None:
        # detect eo finalize function
        if self._mapping is not None and "finalize_function" in self._mapping:
            module_name = self._mapping["finalize_function"]["module"]
            # python function to import from the module
            class_name = self._mapping["finalize_function"]["class"]
            try:
                module = importlib.import_module(module_name)
                try:
                    finalize_class = getattr(module, class_name)
                except AttributeError as exc:
                    raise StoreOpenFailure(
                        f"Class {class_name} not found in module {module_name} for finalize function",
                    ) from exc
            except (
                ImportError,
                ModuleNotFoundError,
                SyntaxError,
                AttributeError,
                PermissionError,
                ValueError,
                TypeError,
                OSError,
                NameError,
            ) as e:
                raise StoreOpenFailure(f"Error while importing module {module_name} : {type(e)} {e}") from e
            if not issubclass(finalize_class, EOSafeFinalize):
                raise StoreOpenFailure(f"{finalize_class} is not implementing EOSafeFinalize")
            self._eo_finalize_function = finalize_class()

    def _detect_external_accessors(self) -> None:
        # detect external eoaccessor
        if self._mapping is not None and "external_accessors" in self._mapping:
            external_accessors: list[dict[str, str]] = self._mapping["external_accessors"]
            for ext_accessor in external_accessors:
                module_name: str = ext_accessor["module"]
                # python function to import from the module
                class_name: str = ext_accessor["class"]
                try:
                    module = importlib.import_module(module_name)
                    try:
                        accessor_class = getattr(module, class_name)
                    except AttributeError as exc:
                        raise StoreOpenFailure(
                            f"Class {class_name} not found in module {module_name} for external accessors function",
                        ) from exc
                except (
                    ImportError,
                    ModuleNotFoundError,
                    SyntaxError,
                    AttributeError,
                    PermissionError,
                    ValueError,
                    TypeError,
                    OSError,
                    NameError,
                ) as e:
                    raise StoreOpenFailure(f"Error while importing module {module_name} : {type(e)} {e}") from e
                if not issubclass(accessor_class, EOAccessor):
                    raise StoreOpenFailure(f"{accessor_class} is not implementing EOAccessor")

    def _extract_internal_data_structure(self, eo_obj_description: dict[str, Any]) -> None:
        """
        extract the info for a given eo_obj_description
        Parameters
        ----------
        eo_obj_description

        Returns
        -------
        None, internal stuff are updated
        """

        target_path = eo_obj_description["target_path"]

        if target_path.startswith(ATTRS_TAG):
            # check and identify patterns of defining attrs
            attrs_pattern_match = match(ATTRS_TARGET_PATH_PATTERN, target_path)
            if attrs_pattern_match is not None:
                eo_path = attrs_pattern_match[1]
                dict_path = attrs_pattern_match[2]
            else:
                raise MappingDefinitionError(
                    f"attributes' target_path: {target_path}; need to match: {ATTRS_TARGET_PATH_PATTERN}",
                    # noqa: E501
                )
            if eo_path not in self._attrs_map:
                self._attrs_map[eo_path] = {}
            if dict_path not in self._attrs_map[eo_path]:
                self._attrs_map[eo_path][dict_path] = []
            self._attrs_map[eo_path][dict_path].append(eo_obj_description)

        elif target_path.startswith(COORDS_TAG):
            # check and identify patterns of defining coords
            coord_with_namespace = match(COORDS_WITH_NAMESPACE_PATTERN, target_path)
            coord_without_namespace = match(COORDS_WITHOUT_NAMESPACE_PATTERN, target_path)
            if coord_with_namespace is not None:
                coord_namespace = coord_with_namespace[1]
            elif coord_without_namespace is not None:
                coord_namespace = DEFAULT_COORDS_NAMESPACE
            else:
                raise MappingDefinitionError(
                    f"coordinates' target_path: {target_path}; "
                    f"need to match: {COORDS_WITH_NAMESPACE_PATTERN} or {COORDS_WITHOUT_NAMESPACE_PATTERN}",
                    # noqa: E501
                )

            # create namespace operations
            if coord_namespace not in self._coords_dict:
                self._coords_dict[coord_namespace] = []

            # add coordinate to namespace
            self._coords_dict[coord_namespace].append(eo_obj_description)
        else:
            self._data_map[target_path] = eo_obj_description

    def _merge_list_attrs(self, list_a: List[Any], list_b: List[Any]) -> List[Any]:
        """Function merging two list of eop attrs recursively.

        Parameters
        ----------
        list_a: List[Any]
            list of attributes
        list_b: List[Any]
            list of attributes

        Returns
        -------
        List[Any]
        """

        len_a = len(list_a)
        len_b = len(list_b)

        # suppose list_a has fewer elements than list_a
        max_common_index = len_a
        if len_a > len_b:
            # when list_b has fewer elements than list a
            max_common_index = len_b

        # update values of common indexes
        for i in range(max_common_index):
            if isinstance(list_a[i], dict) and isinstance(list_b[i], dict):
                list_a[i] = self._merge_dict_attrs(list_a[i], list_b[i])
            elif isinstance(list_a[i], list) and isinstance(list_b[i], list):
                list_a[i] = self._merge_list_attrs(list_a[i], list_b[i])
            else:
                list_a[i] = list_b[i]

        # when list_b has more elements than list_a
        for i in range(max_common_index, len_b):
            list_a.append(list_b[i])

        return list_a

    def _merge_dict_attrs(self, dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> Dict[str, Any]:
        """Function merging two dictionaries of eop attrs recursively.

        Parameters
        ----------
        dict_a: Dict[str, Any]
            dictionary of attributes
        dict_b: Dict[str, Any]
            dictionary of attributes

        Returns
        -------
        Dict[str, Any]
        """

        for k in dict_b.keys():
            if k in dict_a.keys():
                if isinstance(dict_a[k], dict) and isinstance(dict_b[k], dict):
                    dict_a[k] = self._merge_dict_attrs(dict_a[k], dict_b[k])
                elif isinstance(dict_a[k], list) and isinstance(dict_b[k], list):
                    dict_a[k] = self._merge_list_attrs(dict_a[k], dict_b[k])
                else:
                    dict_a[k] = dict_b[k]
            else:
                dict_a[k] = dict_b[k]

        return dict_a

    @staticmethod
    def __get_node_type(attrs: dict[str, Any]) -> str:
        if "other_metadata" in attrs and EOPF_CATEGORY_ATTR in attrs["other_metadata"]:
            if attrs["other_metadata"][EOPF_CATEGORY_ATTR] in (EOCONTAINER_CATEGORY, EOPRODUCT_CATEGORY):
                return attrs["other_metadata"][EOPF_CATEGORY_ATTR]
        return "unknown"

    def load(self, name: Optional[str] = None, **kwargs: Any) -> EOProduct | EOContainer:
        """
        Loads an EOProduct or EOContainer and returns it

        Parameters
        ----------
        name: Optional[str]
            name of the EOProduct or EOContainer loaded
            default None, the EOProduct name is determined from disk storage
        kwargs:
            eop_kwargs: EOProduct init kwargs
            eoc_kwargs: EOContainer init kwargs
            open_kwargs: kwargs for the open function, if open is not called previously
            metadata_only: only create EOProducts/EOContainers with no EOVariables -- in support of ACRI custom converts

        Raises
        -------
        StoreLoadFailure

        Note
        -------
        There is no need to call open function before load, load will do it automatically and pass the open_kwargs

        Returns
        -------
        EOProduct | EOContainer
        """
        # Default name to basename no ext if not provided
        if name is None:
            name = os.path.splitext(self.url.basename)[0]

        if not self.is_open():
            open_kwargs = kwargs.get("open_kwargs", {})
            self.open(mode=OpeningMode.OPEN, **open_kwargs)

        # if the EOProduct has already been loaded
        if self._is_loaded is True and self._root is not None:
            return self._root

        # only to be used when You want just the EOProduct attrs and EOContainers
        metadata_only: bool = kwargs.get("metadata_only", False)

        eop_kwargs = kwargs.pop("eop_kwargs", {})
        eoc_kwargs = kwargs.pop("eoc_kwargs", {})

        eop_mapping_manager = (
            eop_kwargs.get("mapping_factory") or eoc_kwargs.get("mapping_factory") or self._mapping_manager
        )

        processing_version, product_type = self._resolve_type_version()
        self._logger.info(f"Found product type : {product_type} with processing version: {processing_version}")

        try:
            self._root = self._initialize_root(
                eop_kwargs,
                eop_mapping_manager,
                metadata_only,
                name,
                processing_version,
                product_type,
            )
            if self._root is None:
                raise StoreLoadFailure(
                    "The root must be an EOContainer or EOProduct and specified in other_metadata/eopf_category",
                )

            self.__load_fill_root(eop_kwargs, eop_mapping_manager, metadata_only, processing_version, product_type)

            # Finalize the root
            self._finalize_root(eop_kwargs, eop_mapping_manager)
            # Fill the stac id using the default filename convention
            self._fill_stac_id(self._root)

        except Exception as err:
            raise StoreLoadFailure(f"{err}") from err
        finally:
            # mark product as being loaded
            self._is_loaded = True
        self.close_accessors()
        return self._root

    def __load_fill_root(
        self,
        eop_kwargs: dict[Any, Any],
        eop_mapping_manager: EOPFAbstractMappingManager | None,
        metadata_only: bool,
        processing_version: str,
        product_type: str,
    ) -> None:
        if self._root is None:
            raise StoreLoadFailure("root object is None !!!!")

        # determine the length of each attrs eopath
        attrs_eopath_len = {}
        for attr_key in self._attrs_map:
            key_length = len(attr_key.lstrip("/").rstrip("/").split("/"))
            attrs_eopath_len[attr_key] = key_length
        # sort the eopaths by length
        # attributes need to be processed in a hierarhical manner
        sorted_attrs_eopath_len = dict(sorted(attrs_eopath_len.items(), key=lambda item: item[1]))
        # update each eo_object with attrs
        for eo_path in sorted_attrs_eopath_len:
            if eo_path == "/":
                continue

            name = eo_path.rstrip("/").split("/")[-1]

            new_attrs = self[f"attrs:{eo_path}:/"].attrs
            node_type = EOSafeStore.__get_node_type(new_attrs)
            if node_type == "eocontainer":
                self._root[eo_path] = EOContainer(name=name, attrs=new_attrs)
            elif node_type == "eoproduct":
                self._root[eo_path] = EOProduct(
                    name=name,
                    attrs=new_attrs,
                    product_type=product_type,
                    processing_version=processing_version,
                    mapping_manager=eop_mapping_manager,
                    eo_path=eo_path,
                    **eop_kwargs,
                )
            else:
                self._root[eo_path] = EOGroup(name=name, attrs=new_attrs)
        # If has variables
        if not metadata_only:
            self.__load_fill_variables()

    def __load_fill_variables(self) -> None:
        """
        Fill the root with variables

        Returns
        -------

        """
        if self._root is None:
            raise StoreLoadFailure("root object is None !!!!")
        # add each variable to the EOProduct
        for var_path in self.iter(""):
            if var_path not in self._root:
                eov = self[var_path]
                if not is_None_EOObj(eov) and isinstance(eov, EOVariable):
                    self._root[var_path] = eov

    def _resolve_type_version(self) -> Tuple[str, str]:
        processing_version = ""
        product_type = ""
        # determine EOProduct type
        if self._mapping is not None and "recognition" in self._mapping:
            if "product_type" in self._mapping["recognition"]:
                product_type = self._mapping["recognition"]["product_type"]
            if "processing_version" in self._mapping["recognition"]:
                processing_version = self._mapping["recognition"]["processing_version"]
            else:
                processing_version = ""
        return processing_version, product_type

    def _initialize_root(
        self,
        eop_kwargs: dict[str, Any],
        eop_mapping_manager: EOPFAbstractMappingManager,
        metadata_only: bool,
        name: str,
        processing_version: str,
        product_type: str,
    ) -> EOContainer | EOProduct:
        root_obj = self["attrs:/:/"]
        root_node_type = EOSafeStore.__get_node_type(root_obj.attrs)
        if self._eo_init_function is not None:
            self._logger.debug(f"Applying init function from {self._eo_init_function}")
            if root_node_type == "eocontainer":
                return self._eo_init_function.init_container(
                    url=self.url,
                    name=name,
                    product_type=product_type,
                    processing_version=processing_version,
                    attrs=root_obj.attrs,
                    mapping=self._mapping,
                    mapping_manager=eop_mapping_manager,
                    metadata_only=metadata_only,
                    **eop_kwargs,
                )
            elif root_node_type == "eoproduct":
                self._logger.info(f"url: {self.url}")
                return self._eo_init_function.init_product(
                    url=self.url,
                    name=name,
                    attrs=root_obj.attrs,
                    product_type=product_type,
                    processing_version=processing_version,
                    mapping=self._mapping,
                    mapping_manager=eop_mapping_manager,
                    metadata_only=metadata_only,
                    parent=None,
                    **eop_kwargs,
                )
            else:
                raise StoreLoadFailure(
                    "The root must be an EOContainer or EOProduct and specified in other_metadata/eopf_category",
                )
        else:
            if root_node_type == "eocontainer":
                return EOContainer(name=name, type=product_type, attrs=root_obj.attrs)
            elif root_node_type == "eoproduct":
                return EOProduct(
                    name=name,
                    attrs=root_obj.attrs,
                    product_type=product_type,
                    processing_version=processing_version,
                    mapping_manager=eop_mapping_manager,
                    parent=None,
                    **eop_kwargs,
                )
            else:
                raise StoreLoadFailure(
                    "The root must be an EOContainer or EOProduct and specified in other_metadata/eopf_category",
                )

    def _finalize_root(self, eop_kwargs: Any, eop_mapping_manager: EOPFAbstractMappingManager) -> None:
        if self._eo_finalize_function is not None:
            self._logger.debug(f"Applying finalizing function from {self._eo_finalize_function}")
            if isinstance(self._root, EOContainer):
                self._eo_finalize_function.finalize_container(
                    container=self._root,
                    url=self.url,
                    mapping=self._mapping,
                    mapping_manager=eop_mapping_manager,
                    **eop_kwargs,
                )
            elif isinstance(self._root, EOProduct):
                self._eo_finalize_function.finalize_product(
                    eop=self._root,
                    url=self.url,
                    mapping=self._mapping,
                    mapping_manager=eop_mapping_manager,
                    **eop_kwargs,
                )

    def _fill_stac_id(self, eo_object: EOContainer | EOProduct) -> None:
        """
        fill the stac if with the default filename

        Parameters
        ----------
        eo_object

        Returns
        -------

        """
        if isinstance(eo_object, EOContainer):
            for sub in eo_object.values():
                self._fill_stac_id(sub)
        elif isinstance(eo_object, EOProduct):
            try:
                stac_id = eo_object.get_default_file_name_no_extension()
                eo_object._attrs["stac_discovery"]["id"] = stac_id
            except StoreMissingAttr as e:
                self._logger.warning(f"Can't compute stac Id : {e} for product {eo_object.name}")

    # docstr-coverage: inherited
    def __len__(self) -> int:
        self.check_is_opened()
        return super().__len__()

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        # No functionality
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        """No functionality"""
        self.check_is_opened()
        return False

    def is_product(self, path: str) -> bool:
        return (self.url / (path + self.EXTENSION)).isdir()

    # docstr-coverage: inherited
    def write_attrs(self, group_path: str, attrs: MutableMapping[str, Any]) -> None:
        """No functionality"""
        return super().write_attrs(group_path, attrs)

    def __setitem__(self, key: str, value: EOObject, /) -> None:
        return super().__setitem__(key, value)

    def iter(self, _: str) -> Iterator[str]:
        """
        Iterates over the eo_obj descriptions (future EOVariable)

        Returns
        -------
        Iterator[str]
        """
        self.check_is_opened()
        yield from self._data_map

    @staticmethod
    def guess_can_read(file_path: str | AnyPath, **kwargs: Any) -> bool:
        """The given file path is readable or not by this store

        Parameters
        ----------
        file_path: str
            File path to check
        kwargs:
            storage_options: dict arguments for AnyPath

        Returns
        -------
        bool
        """
        url: AnyPath = AnyPath.cast(file_path, **kwargs.get("storage_options", {}))
        if url.path.endswith((".SAFE", ".SAFE.zip", ".SEN3", ".SEN3.zip")):
            return True
        # special case for Sentinel 2 L0
        s2_l0_pattern = r"S2[A-Z]_OPER_MSI_L0__DS_[0-9A-Z]{4}_[0-9]{8}T[0-9]{6}_S[0-9]{8}T[0-9]{6}_N[0-9]{2}\.[0-9]{2}"
        if match(s2_l0_pattern, url.basename):
            return True
        return False

    def close(self, cancel_flush: bool = False) -> None:
        """
        Closes the store
        """
        if self.is_open():
            super().close(cancel_flush=cancel_flush)
            self._is_loaded = False
            self._mapping = {}
            self._eov_kwargs = {}
            self._attrs_map = {}
            self._data_map = {}
            self._coords_dict = {}
            self._root = None
            self.close_accessors()
