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
breakpoint.py

Breakpoin data exporter implementation

"""
import logging
import os
from functools import wraps
from typing import Any, Callable, Optional, Type

import xarray
from xarray.core.datatree import DataTree

from eopf import EOConfiguration, EOContainer
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.exceptions.errors import InvalidConfigurationError
from eopf.product import EOProduct
from eopf.product.eo_group import EOGroup
from eopf.product.eo_variable import EOVariable
from eopf.store.zarr import EOZarrStore

EOConfiguration().register_requested_parameter(
    name="breakpoints__activate_all",
    default_value=False,
    description="Global ON/OFF switch for the breakpoints",
)
EOConfiguration().register_requested_parameter(
    name="breakpoints__folder",
    default_value=os.path.join(os.getcwd(), "breakpoints"),
    param_is_optional=True,
    description="Folder to put breakpoints in",
)
EOConfiguration().register_requested_parameter(
    name="breakpoints__storage_options",
    param_is_optional=True,
    description="storage options in case of S3",
)


##########################
# Data writing functions
##########################


def write_product(
    product: EOProduct,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """Write a product in zarr.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    product: EOProduct
        product to write
    path: str
        uri to the zarr object
    store_params: Any
        parameters to access to the zarr

    Returns
    -------
    None
    """
    store_driver = EOZarrStore
    logger = logging.getLogger("eopf.breakpoint.write_product")
    with store_driver(url=path).open(mode=OpeningMode.CREATE_OVERWRITE) as st:
        out_name = f"{filename_prefix}{product.name}" if filename_prefix is not None else product.name
        logger.info(f"Writing EOProduct breakpoint {path.basename} in {path}")
        st[out_name] = product


def write_container(
    container: EOContainer,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """Write a product in zarr.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    container: EOContainer
        container to write
    path: str
        uri to the zarr object
    store_params: Any
        parameters to access to the zarr

    Returns
    -------
    None
    """
    store_driver = EOZarrStore
    logger = logging.getLogger("eopf.breakpoint.write_product")
    with store_driver(url=path).open(mode=OpeningMode.CREATE_OVERWRITE) as st:
        out_name = f"{filename_prefix}{container.name}" if filename_prefix is not None else container.name
        logger.info(f"Writing breakpoint EOContainer {path.basename} in {path}")
        st[out_name] = container


def write_eogroup(
    eogroup: EOGroup,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """Write a group in zarr.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    eogroup: EOGroup
        group to write
    path: AnyPath
        uri to the zarr object


    Returns
    -------
    None
    """
    store_driver = EOZarrStore
    logger = logging.getLogger("eopf.breakpoint.write_group")
    with store_driver(url=path).open(mode=OpeningMode.CREATE_OVERWRITE) as st:
        out_name = f"{filename_prefix}{eogroup.name}" if filename_prefix is not None else eogroup.name
        logger.info(f"Writing breakpoint EOGroup {out_name} in {path}")
        st[out_name] = eogroup


def write_eovar(
    eovar: EOVariable,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """
    Write a eovar in netcdf.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    eovar: EOVariable
        group to write
    path: AnyPath
        uri to the zarr object


    Returns
    -------
    None
    """
    logger = logging.getLogger("eopf.breakpoint.write_group")
    logger.info(f"Writing EOVariable breakpoint {path / eovar.name}")
    out_name = f"{filename_prefix}{eovar.name}" if filename_prefix is not None else eovar.name
    eovar.data.to_zarr((path / out_name).to_zarr_store())


def write_xarray_dataarray(
    da: xarray.DataArray,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """
    Write an xarray dataarray in zarr.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    da: xarray.DataArray
        group to write
    path: AnyPath
        uri to the zarr object


    Returns
    -------
    None
    """
    logger = logging.getLogger("eopf.breakpoint.write_xarray_dataarray")
    out_name = f"{filename_prefix}{da.name}" if filename_prefix is not None else da.name
    logger.info(f"Writing xarray dataarray breakpoint {path / out_name}")
    da.to_zarr((path / out_name).to_zarr_store())


def write_xarray_datatree(
    da: DataTree,
    path: AnyPath,
    filename_prefix: Optional[str] = None,
) -> None:
    """
    Write an xarray datatree in zarr.

    Parameters
    ----------
    filename_prefix: Optional[str] filename prefix
    da: xarray.DataTree
        group to write
    path: AnyPath
        uri to the zarr object


    Returns
    -------
    None
    """
    logger = logging.getLogger("eopf.breakpoint.write_xarray_datatree")
    out_name = f"{filename_prefix}{da.name}.zarr" if filename_prefix is not None else f"{da.name}.zarr"
    logger.info(f"Writing xarray datatree breakpoint {path / out_name}")
    da.to_zarr((path / out_name).to_zarr_store(), mode="w")


############################
# function writer registry
############################


class TypeFunctionWritersDispatcher:
    """
    Writer handler dispatcher to write breakpoints data

    """

    _type_function_map: dict[Type[Any], Callable[..., Any]] = {
        EOContainer: write_container,
        EOProduct: write_product,
        EOGroup: write_eogroup,
        EOVariable: write_eovar,
        xarray.DataArray: write_xarray_dataarray,
        DataTree: write_xarray_datatree,
    }

    @staticmethod
    def register_handler(type_: Type[Any], func: Callable[..., Any]) -> None:
        """
        Register a new handler for data writing
        Already existing handler can be overloaded

        Function should have this signature ::

                def write_<thing>(
                        data: <thing_type>,
                        path: AnyPath,
                        filename_prefix: Optional[str] = None,
                ) -> None


        Parameters
        ----------
        type_: Type[Any]
             type to register the handler for
        func: Callable
            handler to set

        Returns
        -------
        None
        """
        if not isinstance(type_, type):
            raise TypeError("The first argument must be a type.")
        if not callable(func):
            raise TypeError("The second argument must be a callable.")

        TypeFunctionWritersDispatcher._type_function_map[type_] = func

    @staticmethod
    def handle_value(value: Any, path: AnyPath, filename_prefix: Optional[str] = None) -> None:
        """

        Parameters
        ----------
        value
        path
        filename_prefix

        Returns
        -------

        """
        value_type = type(value)
        real_prefix = filename_prefix if filename_prefix is not None else ""
        if value_type == dict:
            for k, v in value.items():
                TypeFunctionWritersDispatcher.handle_value(v, path, filename_prefix=f"{real_prefix}{k}_")
        elif value_type == list:
            for k, v in enumerate(value):
                TypeFunctionWritersDispatcher.handle_value(v, path, filename_prefix=f"{real_prefix}n{k}_")
        elif value_type in TypeFunctionWritersDispatcher._type_function_map:
            handler = TypeFunctionWritersDispatcher._type_function_map[value_type]
            handler(value, path, filename_prefix)
        else:
            raise TypeError("No handler for this type")


################
# Functions
################


def declare_as_breakpoint(
    data: Any,
    identifier: str,
    description: Optional[str] = None,
    filename_prefix: Optional[str] = None,
) -> Callable[..., Any]:
    """
    Declare a data as a breakpoint.

    Examples
    --------
    ::

            >>> from eopf.computing.breakpoint import declare_as_breakpoint
            >>> pu_out = EOProduct("toto")
            >>> brkp_trigger = declare_as_breakpoint(pu_out, "brkp", "brpk for toto data", "brkp_")
            >>> # ... some other code
            >>> # ... some other code
            >>> brkp_trigger()


    Parameters
    ----------
    data: Any
    identifier: str
    description: Optional[str]
        description of the breakpoint
    filename_prefix: Optional[str]
        prefix to add to the filename

    Returns
    -------
    A callable with no params to trigger the writing when desired
    """
    return eopf_breakpoint_decorator(identifier, description=description, filename_prefix=filename_prefix)(lambda: data)


def get_breakpoints_config() -> dict[str, Any]:
    """
    Get the breakpoints configuration from EOConfiguration
    Returns
    -------
    The breakpoints configuration
    """
    list_of_breakpoints = EOConfiguration().optional_list("breakpoints")
    list_of_breakpoints.discard("breakpoints.activate_all")
    list_of_breakpoints.discard("breakpoints.folder")
    list_of_breakpoints.discard("breakpoints.storage_options")

    return {
        "activate_all": EOConfiguration().get("breakpoints__activate_all", False),
        "folder": EOConfiguration().get("breakpoints__folder", "./breakpoints"),
        "storage_options": EOConfiguration().get("breakpoints__storage_options", ""),
        "ids": {
            k.replace("breakpoints.", ""): EOConfiguration().requested_params_description()["optional"][k][
                "description"
            ]
            for k in list_of_breakpoints
        },
    }


###############
# Decorators
###############


def eopf_breakpoint_decorator(
    identifier: str,
    description: Optional[str] = None,
    filename_prefix: Optional[str] = None,
) -> Callable[..., Any]:
    """A decorator use to wrap callable with break point mechanism


    Parameters
    ----------
    description: Description of the breakpoint
    identifier: name of the breakpoint, you can decorate as many functions as you want with the same identifier
                as long as they write different data
    filename_prefix: prefix for the filename, filenaming convention is up to the data handler



    Returns
    -------
    callable

    Examples
    --------
    >>> from eopf.computing.breakpoint import eopf_breakpoint_decorator
    >>> from eopf.product import EOGroup, EOProduct
    >>> @eopf_breakpoint_decorator("my_function", description="export foobar data", filename_prefix="foobar_")
    ... def my_function(groups: list[EOGroup]) -> dict[str,EOProduct]:
    ...    product = EOProduct("new_product")
    ...    for group in groups:
    ...        product[group.name] = group
    ...    return {"out": product}
    """
    if identifier in ["activate_all", "folder"]:
        raise InvalidConfigurationError(f"{identifier} is not allowed for breakpoint name")

    EOConfiguration().register_requested_parameter(
        f"breakpoints__{identifier}",
        default_value=False,
        param_is_optional=True,
        description=description,
    )

    def decorator(func_in: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func_in)
        def _method_wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            logger = logging.getLogger("eopf.breakpoint")

            if not bool(EOConfiguration().get("breakpoints__activate_all", default=False)):
                if not bool(EOConfiguration().get(f"breakpoints__{identifier}", default=False)):
                    logger.debug(f"Breakpoint {identifier} is deactivated")
                    return func_in(*args, **kwargs)

            if EOConfiguration().has_value("breakpoints__folder"):
                brkp_path = EOConfiguration().get("breakpoints__folder")
                brkp_storage_options = EOConfiguration().get("breakpoints__storage_options", {})
                brkp_storage_options = brkp_storage_options if brkp_storage_options is not None else {}
                breakpoint_folder = AnyPath.cast(f"{brkp_path}/{identifier}", **brkp_storage_options)
            else:
                breakpoint_folder = AnyPath.cast(os.getcwd()) / "breakpoints" / identifier
            breakpoint_folder.mkdir(exist_ok=True)
            if not breakpoint_folder.islocal():
                (breakpoint_folder / "placeholder.txt").touch()
            logger.debug(f"WRITE Breakpoint for {func_in.__name__} in {breakpoint_folder}")
            obj = func_in(*args, **kwargs)
            try:
                TypeFunctionWritersDispatcher.handle_value(obj, breakpoint_folder, filename_prefix)
            except Exception as err:
                logger.error(err)
                raise err

            return obj

        return _method_wrapper

    return decorator
