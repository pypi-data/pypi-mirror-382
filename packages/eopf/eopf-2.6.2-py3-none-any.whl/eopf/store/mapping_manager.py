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
mapping_manager.py

mapping manager implementation

"""
import copy
import re
from abc import ABC, abstractmethod
from ast import literal_eval
from datetime import datetime
from functools import reduce
from os.path import basename
from typing import Any, Callable, Dict, List, Optional, Type, Union

from lxml import etree

from eopf.common.constants import NO_PATH_MATCH
from eopf.common.file_utils import AnyPath
from eopf.exceptions.errors import (
    MappingConfigurationError,
    MappingFormatterError,
    MappingMissingError,
    MissingArgumentsMappingFormatterError,
)
from eopf.store.mapping_factory import EOPFAbstractMappingFactory, EOPFMappingFactory


class AbstractMappingFormatter(ABC):

    @abstractmethod
    def format(self, **kwargs: Any) -> Any:
        pass


class MappingFormatterFactory:
    """
    Mapping formatter factory
    """

    formatters: dict[str, Type[AbstractMappingFormatter]] = {}

    def __new__(cls, *args: Any, **kwargs: Any) -> None:
        raise TypeError("MappingFormatterFactory can not be instantiated : static class !!")

    @classmethod
    def register_formatter(
        cls,
        name: str,
    ) -> Callable[[Type[AbstractMappingFormatter]], Type[AbstractMappingFormatter]]:
        """
        Register a formatter

        Parameters
        ----------
        name

        Returns
        -------

        """

        def inner_register(wrapped: Type[AbstractMappingFormatter]) -> Type[AbstractMappingFormatter]:
            cls.formatters[name] = wrapped
            return wrapped

        return inner_register

    @classmethod
    def get_formmater(cls, name: str) -> Optional[Type[AbstractMappingFormatter]]:
        """
        Get a formatter based on the name
        Parameters
        ----------
        name

        Returns
        -------

        """
        if name in cls.formatters:
            return cls.formatters[name]

        return None


@MappingFormatterFactory.register_formatter("find")
class FindFormatter(AbstractMappingFormatter):
    """
    Find formatter

    Find files using the pattern
    """

    def format(self, **kwargs: Any) -> str:
        """
        Apply the formatter
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        if "product_url" not in kwargs:
            raise MissingArgumentsMappingFormatterError("product_url missing")

        if "pattern" not in kwargs:
            raise MissingArgumentsMappingFormatterError("pattern missing")

        # retrieve necessary input
        product_url: AnyPath = kwargs["product_url"]
        pattern: str = kwargs["pattern"]

        try:
            # find all files matching the pattern
            files: list[AnyPath] = product_url.find(pattern)
            if len(files) == 0:
                return NO_PATH_MATCH

            # get relative path to the product url respective for the first file
            # we do not need the entire path since the accessor will know the product_url also
            file = files[0].relpath(product_url)
            return file
        except Exception as err:
            raise MappingFormatterError(f"{err}") from err


@MappingFormatterFactory.register_formatter("copy")
class CopyFormmater(AbstractMappingFormatter):
    """
    Copy a section of the mapping to this place
    """

    def format(self, **kwargs: Any) -> dict[str, Any]:
        """
        Apply the formatter
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        if "map" not in kwargs:
            raise MissingArgumentsMappingFormatterError("map missing")

        return kwargs["map"]


@MappingFormatterFactory.register_formatter("is_optional")
class IsOptionalFormmater(AbstractMappingFormatter):
    """
    IsOptional allows a node to be optional
    """

    def format(self, **kwargs: Any) -> dict[str, Any]:
        """
        If a key is not present in the eo_obj_description or the value of the key is equal to value,
        the eo_obj_description will not be added in the parsed map
        """

        if "eo_obj_description" not in kwargs:
            raise MissingArgumentsMappingFormatterError("eo_obj_description missing")
        eo_obj_description = kwargs["eo_obj_description"]

        if "key" not in kwargs:
            raise MissingArgumentsMappingFormatterError("key missing")
        key = kwargs["key"]

        if "value" not in kwargs:
            raise MissingArgumentsMappingFormatterError("value missing")
        value = kwargs["value"]

        if key in eo_obj_description and eo_obj_description[key] != value:
            return eo_obj_description
        return {}


@MappingFormatterFactory.register_formatter("unroll")
class UnrollFormmater(AbstractMappingFormatter):
    """
    Unroll formatter

    unroll a mapping by applying unroll parameters
    """

    def format(self, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Apply the formatter
        Parameters
        ----------
        kwargs

        Returns
        -------

        """

        def _recursive_replace(data_in: Any, replace_dict: dict[str, str]) -> Any:
            if isinstance(data_in, list):
                for idx, val in enumerate(data_in):
                    if isinstance(val, str):
                        for to_replace, new_value in replace_dict.items():
                            data_in[idx] = val.replace(to_replace, new_value.lower())
                    else:
                        data_in[idx] = _recursive_replace(val, replace_dict)
            elif isinstance(data_in, dict):
                for k, v in data_in.items():
                    if isinstance(v, str):
                        for to_replace, new_value in replace_dict.items():
                            if k != "source_path":
                                v = v.replace(to_replace, new_value.lower())
                            else:
                                v = v.replace(to_replace, new_value)
                        data_in[k] = v
                    else:
                        data_in[k] = _recursive_replace(v, replace_dict)

            return data_in

        if "json_data_in" not in kwargs:
            raise MissingArgumentsMappingFormatterError("json_data_in missing")

        if "unroll_vars" not in kwargs:
            raise MissingArgumentsMappingFormatterError("unroll_vars missing")

        json_data_in = kwargs["json_data_in"]
        unroll_vars = kwargs["unroll_vars"]

        list_eoobj_descriptions: list[dict[str, Any]] = []
        list_vars_to_replace = list(unroll_vars.keys())

        if len(list_vars_to_replace) == 1:
            # unrolls based on two variables
            var_to_replace = list_vars_to_replace[0]
            for new_val in unroll_vars[var_to_replace]:
                replace_dict = {var_to_replace: new_val}
                data_in = copy.deepcopy(json_data_in)
                variable_description = _recursive_replace(data_in, replace_dict)
                list_eoobj_descriptions.append(variable_description)

        elif len(list_vars_to_replace) == 2:
            # unrolls based on one variable
            var_to_replace1 = list_vars_to_replace[0]
            var_to_replace2 = list_vars_to_replace[1]
            for new_val_1 in unroll_vars[var_to_replace1]:
                for new_val_2 in unroll_vars[var_to_replace2]:
                    replace_dict = {}
                    replace_dict[var_to_replace1] = new_val_1
                    replace_dict[var_to_replace2] = new_val_2
                    data_in = copy.deepcopy(json_data_in)
                    variable_description = _recursive_replace(data_in, replace_dict)
                    list_eoobj_descriptions.append(variable_description)

        else:
            raise MappingFormatterError("just 1d and 2d unrolls are supported")

        return list_eoobj_descriptions


def recursive_replace(eo_obj_template: Dict[str, Any], replace_map: Dict[str, str]) -> Dict[str, Any]:
    """
    Recursive replace
    Parameters
    ----------
    eo_obj_template
    replace_map

    Returns
    -------

    """
    new_eo_obj_template = {}
    for key, value in eo_obj_template.items():
        # replace key
        new_key = key
        for k, v in replace_map.items():
            new_key = new_key.replace(k, v)
        # replace value
        new_value = value
        if isinstance(value, dict):
            new_value = recursive_replace(value, replace_map)
        elif isinstance(value, str):
            for k, v in replace_map.items():
                new_value = new_value.replace(k, v)
        elif isinstance(value, list):
            new_value = []
            for element in value:
                new_element = element
                if isinstance(element, str):
                    for k, v in replace_map.items():
                        new_element = new_element.replace(k, v)
                new_value.append(new_element)
        new_eo_obj_template[new_key] = new_value
    return new_eo_obj_template


def zip_unroll(eo_obj_template: Dict[str, Any], unroll_map: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """

    Parameters
    ----------
    eo_obj_template
    unroll_map

    Returns
    -------

    """
    # initialize output templates
    unrolled_eo_obj_templates = []

    # zip template variables
    key_values_lst = [[{key: v} for v in values] for key, values in unroll_map.items()]
    # [{key: values}]
    keys_value_lst = [reduce(lambda x, y: x | y, key_values) for key_values in zip(*key_values_lst)]
    # [{key1: value, key2: value}]

    # replace variables
    for replace_map in keys_value_lst:
        unrolled_eo_obj_templates += [recursive_replace(eo_obj_template, replace_map)]

    return unrolled_eo_obj_templates


SAFE_RE = r"S([1-6])(\w)_(\w{2})_(\w{3})\w_(\w{4})_(.*)_(.*)_(.*)_(.*)_(.*)\.SAFE"
SAFE_DATA_RE = r".*(s[1-6].-.*)\.[xml|tiff|nc]"


@MappingFormatterFactory.register_formatter("find_unroll")
class FindUnrollFormatter(AbstractMappingFormatter):
    """
    Find product and unroll
    """

    def format(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Apply the formatter
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        required_kwargs = {"product_url", "pattern", "json_data_in"}
        if missing_kwargs := required_kwargs.difference(kwargs.keys()):
            raise MissingArgumentsMappingFormatterError(f"{','.join(missing_kwargs)} missing")

        # extract info from SAFE
        safe_fn = kwargs["product_url"].path.split("/")[-1]
        (
            satellite,
            platform,
            acquisition_mode,
            product_type,
            _,
            start_time,
            end_time,
            absolute_orbit_number,
            mission_data_take_id,
            product_unique_id,
        ) = re.match(
            SAFE_RE,
            safe_fn,
        ).groups()  # type: ignore

        date_fmt = "%Y%m%dT%H%M%S"
        duration = datetime.strptime(end_time, date_fmt) - datetime.strptime(start_time, date_fmt)
        relative_orbit_number = (int(absolute_orbit_number) - 73) // 175 + 1

        product_base_name = (
            f"S0{satellite}S{acquisition_mode}{product_type}_{start_time}"
            f"_{duration.seconds:04}_{platform}{relative_orbit_number:03}"
            f"_{product_unique_id}_{mission_data_take_id}"
        )

        # find paths
        safe_data_files: list[AnyPath] = kwargs["product_url"].find(kwargs["pattern"])
        if len(safe_data_files) == 0:
            is_optional = kwargs.get("json_data_in", {}).get("is_optional", False)
            if is_optional is False:
                raise FileNotFoundError("NO FILE/DIR MATCH")
        safe_data_relpaths = sorted(
            [file.relpath(reference=kwargs["product_url"]) for file in safe_data_files],
            key=lambda relpath: relpath[-7:],
        )

        # extract product names
        product_names, acquisition_mode_numbers, annotation_relpaths = [], [], []
        for safe_data_relpath in safe_data_relpaths:
            safe_data_fn = re.match(SAFE_DATA_RE, str(safe_data_relpath)).groups()[0]  # type: ignore
            safe_data_attrs = safe_data_fn.split("-")
            acquisition_mode_number, polarisation, product_number = (
                safe_data_attrs[1],
                safe_data_attrs[3],
                safe_data_attrs[-1],
            )
            product_name = f"{product_base_name}_{polarisation}"
            if acquisition_mode == "WV":
                product_name = f"{product_name}_{acquisition_mode_number}_{product_number}"
            elif product_type == "SLC" and acquisition_mode in ["IW", "EW"]:
                product_name = f"{product_name}_{acquisition_mode_number}"

            product_names.append(product_name.upper())
            annotation_relpaths.append(f"annotation/{basename(safe_data_fn)}.xml")
            acquisition_mode_numbers.append(acquisition_mode_number)

        unroll_vars = {
            "{{product_name}}": product_names,
            "{{product_path}}": safe_data_relpaths,
            "{{annotation_path}}": annotation_relpaths,
            "{{acquisition_mode}}": acquisition_mode_numbers,  # FIXME this is swath
        }
        eo_obj_templates = zip_unroll(eo_obj_template=kwargs["json_data_in"], unroll_map=unroll_vars)

        return eo_obj_templates


@MappingFormatterFactory.register_formatter("burst_unroll")
class BurstFormatter(FindUnrollFormatter):
    """
    Unroll for burst version
    """

    def format(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Apply the formatter
        Parameters
        ----------
        kwargs

        Returns
        -------

        """
        product_eo_obj_templates = super().format(**kwargs)  # eo_obj_templates with products unrolled
        product_burst_eo_obj_templates = []  # eo_obj_templates with products and bursts unrolled

        for product_eo_obj_template in product_eo_obj_templates:

            source_path = product_eo_obj_template["source_path"].partition(":")[0]
            product_name = re.match(SAFE_DATA_RE, source_path).groups()[0]  # type: ignore
            swath = product_name.split("-")[1].upper()

            # parse annotation file
            if "measurement/" in source_path or "calibration/" in source_path:
                annotation_path = kwargs["product_url"] / f"annotation/{product_name}.xml"
            else:
                annotation_path = kwargs["product_url"] / source_path

            with annotation_path.open("r") as fin:
                annotation_tree = etree.parse(fin)

            # find bursts and replace placeholders
            burst_idx = 0
            bursts: Any = annotation_tree.xpath("//product/swathTiming/burstList/burst")
            if not isinstance(bursts, list):
                bursts = list(bursts)
            for burst in bursts:
                burst_id = burst.xpath("burstId")[0].text if burst.xpath("burstId") else str(burst_idx + 1)
                product_burst_eo_obj_template = recursive_replace(
                    eo_obj_template=product_eo_obj_template,
                    replace_map={
                        "{{swath}}": swath,
                        "{{burst_idx}}": str(burst_idx),
                        "{{burst_id}}": f"{burst_id:06}",
                    },
                )
                product_burst_eo_obj_templates.append(product_burst_eo_obj_template)
                burst_idx += 1

        return product_burst_eo_obj_templates


class EOPFAbstractMappingManager(ABC):
    """
    Mapping manager abstract base class
    """

    @abstractmethod
    def parse_mapping(
        self,
        product_url: Optional[Union[AnyPath, str]] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        **kwargs: Any,
    ) -> tuple[Optional[dict[str, Any]], Optional[list[tuple[str, str]]]]:
        """
        Parse a mapping

        Parameters
        ----------
        product_url
        product_type
        processing_version
        kwargs

        Returns
        -------

        """

    @abstractmethod
    def parse_shortnames(
        self,
        product_url: Optional[Union[AnyPath, str]] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[list[tuple[str, str]]]:
        """
        Parse shortname
        Parameters
        ----------
        product_url
        product_type
        processing_version
        kwargs

        Returns
        -------

        """


class EOPFMappingManager(EOPFAbstractMappingManager):
    """
    Mapping manager implementation
    """

    FORMATTER_PATTERN = r"^@#(.*)({.*})#@$"
    CURRENT_MAPPING_REFERENCE = r"^<SELF\[(.*)\]>$"
    CURRENT_KEY_VALUE_REFERENCE = r"^<VALUE>$"
    CURRENT_PRODUCT_REFERENCE = r"^<URL>$"
    ENTIRE_MAP_REFERENCE = "/"

    def __init__(self, mapping_factory: Optional[EOPFAbstractMappingFactory] = None) -> None:
        self._map: dict[str, Any] = {}
        self._url: Optional[AnyPath] = None
        self._type: Optional[str] = ""
        self._mapping_formatter_factory = MappingFormatterFactory
        self._mapping_factory = mapping_factory if mapping_factory is not None else EOPFMappingFactory()

    def _parse_formatter_parameters(
        self,
        formatter_parameters: dict[str, Any],
        key_value: Optional[Any],
    ) -> dict[str, Any]:
        """
        Parse a formatter parameters

        Parameters
        ----------
        formatter_parameters
        key_value

        Returns
        -------

        """
        for k, v in formatter_parameters.items():
            # get other information from the initial unparser mapping
            match = re.match(self.CURRENT_MAPPING_REFERENCE, v)
            if match:
                reference_path = match[1]
                if reference_path == self.ENTIRE_MAP_REFERENCE:
                    # if one passes "/" we get the entire map
                    formatter_parameters[k] = self._map
                else:
                    # if one passes /key/sub_key it will get the values of the sub_key
                    keys = reference_path.split("/")
                    tmp = self._map
                    while len(keys) > 0:
                        cur_key = keys.pop(0)
                        tmp = tmp[cur_key]
                    formatter_parameters[k] = tmp

            # get the value of the key identified as formmater
            match = re.match(self.CURRENT_KEY_VALUE_REFERENCE, v)
            if match:
                formatter_parameters[k] = key_value

            # get the value of the key identified as formmater
            match = re.match(self.CURRENT_PRODUCT_REFERENCE, v)
            if match:
                if self._url is None:
                    raise MappingConfigurationError(
                        f"Url is requested with this mapping to apply formatters : {self._type}",
                    )
                formatter_parameters[k] = self._url

        return formatter_parameters

    def _parse_data_mapping(self, data_mapping: list[dict[str, Any]], **kwargs: Any) -> list[dict[str, Any]]:
        """
        Parse a mapping
        Parameters
        ----------
        data_mapping
        kwargs

        Returns
        -------

        """
        parsed_data_map: list[dict[str, Any]] = []

        for var_description in data_mapping:
            # we expect formatter of entire description dicts to have only one key
            if len(var_description) == 1:
                (k, v) = var_description.popitem()
                match = re.match(self.FORMATTER_PATTERN, k)
                if not match:
                    # a var description should have multiple keys, however in the future it
                    # may be possible to descripe a variable with one key
                    parsed_data_map.append(var_description)
                else:
                    formmater_name: str = match[1]
                    formatter: Optional[type[AbstractMappingFormatter]] = self._mapping_formatter_factory.get_formmater(
                        formmater_name,
                    )
                    # In case of short names we skip the find formatter not to need a real product file
                    if isinstance(formatter, FindFormatter) and "shortnames_mode" in kwargs:
                        parsed_data_map.append(var_description)
                        break

                    raw_formatter_parameters: dict[str, Any] = literal_eval(match[2])
                    parsed_formmatter_parameters = self._parse_formatter_parameters(
                        formatter_parameters=raw_formatter_parameters,
                        key_value=v,
                    )

                    if formatter is not None:
                        formmater_result = formatter().format(**parsed_formmatter_parameters)
                        if isinstance(formmater_result, dict) and (len(formmater_result) > 0):
                            # in case only one var description is returned
                            parsed_data_map.append(formmater_result)
                        elif isinstance(formmater_result, list):
                            # in case multiple var descriptions are returned
                            parsed_data_map.extend(formmater_result)
                        else:
                            pass
            else:
                # just a normal var description
                parsed_data_map.append(var_description)

        return parsed_data_map

    def _parse_map_values(self, mapping: dict[str, Any] | list[Any], **kwargs: Any) -> dict[str, Any] | list[Any]:
        if isinstance(mapping, dict):
            return self._parse_map_dict_values(mapping, **kwargs)

        if isinstance(mapping, list):
            for idx, val in enumerate(mapping):
                mapping[idx] = self._parse_map_values(val, **kwargs)
        return mapping

    def _parse_map_dict_values(self, mapping: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        for k, v in mapping.items():
            # apply formmater for the values
            if isinstance(v, str):
                match = re.match(self.FORMATTER_PATTERN, v)
                if match:
                    formmater_name: str = match[1]
                    formatter: Optional[type[AbstractMappingFormatter]] = self._mapping_formatter_factory.get_formmater(
                        formmater_name,
                    )
                    # In case of short names we skip the find formatter not to need a real product file
                    if formatter is FindFormatter and "shortnames_mode" in kwargs:
                        mapping[k] = match[2]
                        break

                    raw_formatter_parameters: dict[str, Any] = literal_eval(match[2])
                    parsed_formmatter_parameters = self._parse_formatter_parameters(raw_formatter_parameters, None)

                    if formatter is not None:
                        mapping[k] = formatter().format(**parsed_formmatter_parameters)
            elif isinstance(v, dict):
                mapping[k] = self._parse_map_values(v, **kwargs)
            elif isinstance(v, list):
                mapping[k] = self._parse_map_values(v, **kwargs)
            else:
                mapping[k] = v
        return mapping

    def _parse_map(self, mapping: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        parsed_map = self._parse_map_dict_values(mapping, **kwargs)
        data_mapping = parsed_map["data_mapping"]
        parsed_data_mapping = self._parse_data_mapping(data_mapping, **kwargs)
        parsed_map["data_mapping"] = parsed_data_mapping

        return parsed_map

    def _get_short_names(self, mapping: dict[str, Any]) -> list[tuple[str, str]]:
        short_names: list[tuple[str, str]] = []

        if "data_mapping" in mapping:
            for eo_obj_description in mapping["data_mapping"]:
                if "target_path" in eo_obj_description:
                    if eo_obj_description["target_path"].startswith(("attrs:", "coords:")):
                        continue
                    if "short_name" in eo_obj_description:
                        short_name = eo_obj_description["short_name"]
                        short_names.append((short_name, eo_obj_description["target_path"]))

        return short_names

    def parse_mapping(
        self,
        product_url: Optional[Union[AnyPath, str]] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        **kwargs: Any,
    ) -> tuple[Optional[dict[str, Any]], Optional[list[tuple[str, str]]]]:
        """
        Retrieve the map and parse it

        Parameters
        ----------
        product_url : Optional[Union[AnyPath, str]]
            path to the product, needed for the find formatters in the mapping
        product_type: Optional[str] = None
            the type of the product
        processing_version: Optional[str] = None
            the processing_version of the product_type
        kwargs:
            kwargs relevant to AnyPath

        Returns
        -------
        tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]

        """
        self._type = product_type
        # retrieve the product name from the path
        if product_url is not None:
            self._url = AnyPath.cast(product_url, kwargs=kwargs)

        # get the unparsed map from the factory
        try:
            unparsed_map: dict[str, Any] | None = self._mapping_factory.get_mapping(
                product_path=self._url,
                product_type=product_type,
                processing_version=processing_version,
            )
        except MappingMissingError:
            unparsed_map = None

        if unparsed_map is not None:
            self._map = unparsed_map
            parsed_map: dict[str, Any] = self._parse_map(unparsed_map)
            short_names: list[tuple[str, str]] = self._get_short_names(parsed_map)
            return parsed_map, short_names
        return None, None

    def parse_shortnames(
        self,
        product_url: Optional[Union[AnyPath, str]] = None,
        product_type: Optional[str] = None,
        processing_version: Optional[str] = None,
        **kwargs: Any,
    ) -> Optional[list[tuple[str, str]]]:
        """
        Retrieve the map and return short_names dict

        Parameters
        ----------
        product_url : Optional[Union[AnyPath, str]]
            path to the product, needed for the find formatters in the mapping
        product_type: Optional[str] = None
            the type of the product
        processing_version: Optional[str] = None
            the processing_version of the product_type
        kwargs:
            kwargs relevant to AnyPath

        Returns
        -------
        Optional[dict[str, str]]

        """
        # retrieve the product name from the path
        if product_url is not None:
            self._url = AnyPath.cast(product_url, kwargs=kwargs)
        self._type = product_type
        # get the unparsed map from the factory, we only have the type in our case
        try:
            unparsed_map: dict[str, Any] | None = self._mapping_factory.get_mapping(
                product_path=self._url,
                product_type=product_type,
                processing_version=processing_version,
            )
        except MappingMissingError:
            unparsed_map = None

        if unparsed_map is not None:
            self._map = unparsed_map
            parsed_map: dict[str, Any] = self._parse_map(unparsed_map, shortnames_mode=True)
            short_names: list[tuple[str, str]] = self._get_short_names(parsed_map)
            return short_names
        return None
