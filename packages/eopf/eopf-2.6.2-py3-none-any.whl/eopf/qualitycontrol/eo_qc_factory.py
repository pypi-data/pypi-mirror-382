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

eo_qc_factory.py

Factory pattern for the quality checks

"""

from typing import Any, Callable, Self, Type

import dacite
import numpy as np
from dacite import Config, MissingValueError

from eopf.exceptions.errors import EOQCError
from eopf.qualitycontrol.eo_qc import EOQC


class EOQCFactory:
    """
    Actual EOQCFactory class to register checks constructors and get them

    """

    qc_dict: dict[str, Type[EOQC]] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        """
        Static class lock

        Parameters
        ----------
        args : Any
        kwargs : Any
        """
        raise TypeError("EOStoreFactory can not be instantiated : static class !!")

    @classmethod
    def register_eoqc(cls, name: str) -> Callable[[Type[EOQC]], Type[EOQC]]:
        """
        Class decorator to register an EOQC in the factory
        Parameters
        ----------
        name : str, name to register it

        Returns
        ---------
        Wrapped class, without behaviour modification

        """

        def inner_register(wrapped: Type[EOQC]) -> Type[EOQC]:
            cls.qc_dict[name] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_eoqc_type(cls, eoqc_name: str) -> Type[EOQC]:
        """
        Get the EOQC for this name

        Parameters
        ----------
        eoqc_name

        Returns
        -------
        The EOQC constructor
        """
        if eoqc_name in cls.qc_dict:
            return cls.qc_dict[eoqc_name]
        raise KeyError(f"No registered eoqc with name : {eoqc_name}")

    @classmethod
    def get_eoqc_instance(cls, eoqc_name: str, data: dict[str, Any]) -> EOQC:
        """
        Get the EOQC for this name

        Parameters
        ----------
        data
        eoqc_name

        Returns
        -------

        """
        eoqc_type = EOQCFactory.get_eoqc_type(eoqc_name)
        try:
            eoqc = dacite.from_dict(eoqc_type, data, config=Config(type_hooks={np.float64: np.float64}))
        except MissingValueError as e:
            raise EOQCError(f"Missing element in configuration to instance {eoqc_type} : {e}") from e
        return eoqc

    @classmethod
    def get_eoqc_available(cls) -> dict[str, Type[EOQC]]:
        """
        Get the dict of the available eoqc registrered in the factory
        Returns
        -------
        the dict[name, EOQC] of registered factory

        """
        out_dict = {}
        for name, val in cls.qc_dict.items():
            out_dict[f"{name}"] = val
        return out_dict

    @classmethod
    def check_eoqc_available(cls, name: str) -> bool:
        """
        Check if a specific eoqc is registered
        Parameters
        ----------
        name : str, name of the check

        Returns
        -------
        Boolean, true if available, false else
        """
        return name in cls.qc_dict
