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
store_factory.py

EOProductStore yet an other factory pattern

"""
from typing import Any, Callable, Optional, Type

from eopf.common.file_utils import AnyPath
from eopf.exceptions.errors import EOStoreFactoryNoRegisteredStoreError
from eopf.store import EOProductStore


class EOStoreFactory:
    """ "
    The EOProductStore factory impl
    """

    product_formats: dict[str, Type[EOProductStore]] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> None:
        raise TypeError("EOStoreFactory can not be instantiated : static class !!")

    @classmethod
    def register_store(cls, product_format: str) -> Callable[[Type[EOProductStore]], Type[EOProductStore]]:
        """
        Register a store
        Parameters
        ----------
        product_format

        Returns
        -------

        """

        def inner_register(wrapped: Type[EOProductStore]) -> Type[EOProductStore]:
            cls.product_formats[product_format] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_product_store_by_file(
        cls,
        file_path: str | AnyPath,
        storage_options: Optional[dict[str, Any]] = None,
    ) -> Type[EOProductStore]:
        """
        Get the store able to read this file, file need to exist
        Parameters
        ----------
        file_path

        Returns
        -------

        """
        kwargs = {} if storage_options is None else storage_options
        file_path_any = AnyPath.cast(file_path, **kwargs)
        for store_type in cls.product_formats.values():
            if store_type.guess_can_read(file_path_any):
                return store_type
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store compatible with : {file_path_any}")

    @classmethod
    def get_product_store_by_filename(cls, file_path: str) -> Type[EOProductStore]:
        """
        Get the store able to read this filename, this is a simple dummy test on the filename
        Parameters
        ----------
        file_path

        Returns
        -------

        """
        for store_type in cls.product_formats.values():
            if store_type.is_valid_url(file_path):
                return store_type
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store compatible with filename : {file_path}")

    @classmethod
    def get_product_store_by_format(cls, item_format: str) -> Type[EOProductStore]:
        """
        Get the product store by asking with a specific format ( zarr etc)
        Parameters
        ----------
        item_format

        Returns
        -------

        """
        if item_format in cls.product_formats:
            return cls.product_formats[item_format]
        raise EOStoreFactoryNoRegisteredStoreError(f"No registered store with format : {item_format}")

    @classmethod
    def get_product_stores_available(cls) -> dict[str, Type[EOProductStore]]:
        """
        Get the available product store dict
        Returns
        -------

        """
        out_dict = {}
        for mapping, store in cls.product_formats.items():
            out_dict[f"{mapping}"] = store
        return out_dict

    @classmethod
    def check_product_store_available(cls, item_format: str) -> bool:
        """
        Test if a product store is available to handle this format
        Parameters
        ----------
        item_format

        Returns
        -------

        """
        return item_format in cls.product_formats
