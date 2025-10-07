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
xml_accessors.py

XML acessors implementations

"""
import re
from abc import ABC
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)
from weakref import WeakValueDictionary

import lxml
import lxml.etree
import numpy as np
import xarray as xr
from jinja2 import Environment, FileSystemLoader

from eopf import EOGroup
from eopf.accessor import EOAccessor, EOAccessorFactory
from eopf.accessor.abstract import EOReadOnlyAccessor
from eopf.accessor.netcdf_accessors import EONetCDFAccessor
from eopf.common import xml_utils
from eopf.common.constants import OpeningMode
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import not_none
from eopf.common.type_utils import Chunk
from eopf.exceptions import (
    MissingConfigurationParameterError,
    XmlManifestNetCDFError,
    XmlParsingError,
)
from eopf.exceptions.errors import MissingArgumentError, XmlXpathError
from eopf.formatting import EOFormatterFactory
from eopf.formatting.misc_formatters import ToImageSize
from eopf.formatting.xml_formatters import (
    ToProcessingHistoryS01,
    ToProcessingHistoryS03,
    ToS02Adfs,
)
from eopf.logging.log import EOLogging
from eopf.product.eo_variable import EOVariable

if TYPE_CHECKING:  # pragma: no cover
    from eopf.product.eo_object import EOObject


class AbstractXMLAccessor(EOReadOnlyAccessor, ABC):  # pragma: no cover
    """Abstract XML Accessor"""

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self._root: Optional[lxml.etree._ElementTree] = None


class AbstractXMLWithNamespacesAccessor(AbstractXMLAccessor, ABC):  # pragma: no cover
    """Abstract XML Accessor with namespaces for XPath request"""

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self._namespaces: dict[str, str] = {}

    def xpath(self, _path: str) -> Any:
        """
        Apply a xpath and return the request result

        Parameters
        ----------
        _path

        Returns
        -------

        """
        self.check_is_opened()
        if self._root is None:
            raise AttributeError("Document should be parsed")

        return xml_utils.get_xpath_results(self._root, _path, self._namespaces)


class AbstractXMLCommonOpenAccessor(AbstractXMLWithNamespacesAccessor, ABC):  # pragma: no cover
    """Abstract XML Accessor with namespaces and common open method"""

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        Parameters
        ----------
        mode: OpeningMode
        chunk_sizes: Optional[Chunk]
        kwargs: Any

        Kwargs
        -------
        Should contain at least these elements:
        - "namespace" : list of etree namespaces to apply to the xml file
        """

        super().open(chunk_sizes=chunk_sizes, mode=mode)

        if not self.url.isfile():
            raise FileNotFoundError(f"Can't find file at {self.url}")

        # Recover configuration
        with self.url.open("r") as xml_fobj:
            try:
                self._root = xml_utils.parse_xml(xml_fobj)
            except Exception as e:
                raise XmlParsingError(f"Exception while parsing xml: {e}") from e
        if "namespace" not in kwargs:
            raise TypeError("Missing configuration parameter: 'namespace'")
        self._namespaces = kwargs["namespace"]

        return self


@EOAccessorFactory.register_accessor("xmlmultifiles")
class XMLMultipleFilesAccessor(EOReadOnlyAccessor):
    """Store representation to access multiple XML files and convert their fields in N-dimensional variables

    Inherits from EOAccessor

    Parameters
    ----------
    url: str
        path url or the target accessor

    Attributes
    ----------
    url: str
        url to the target accessor
    """

    _dynamic_params: list[str] = ["target_type", "source_order"]

    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._root: List[lxml.etree._ElementTree] = []
        self.urls: List[AnyPath] = [p for p in self.url.glob("") if p.isfile()]
        if len(self.urls) == 0:
            raise FileNotFoundError(f"No files found in {url}")
        self._source_order: List[str] = []
        self._target_type: Dict[str, Any] = {}
        self._is_array = False

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the store in the given mode

        Parameters
        ----------
        mode: str, optional
            mode to open the store
        **kwargs: Any
            extra kwargs of open on library used
        """

        super().open(chunk_sizes=chunk_sizes, mode=mode)

        try:
            self._source_order = kwargs["source_order"]
            self._target_type = kwargs["target_type"]
        except KeyError as e:
            raise TypeError(f"Missing configuration parameter: {e}") from e

        self._sort_source_urls()
        self._root = []
        for url in self.urls:
            with url.open() as xml_fobj:
                self._root.append(xml_utils.parse_xml(xml_fobj))
        return self

    def _sort_source_urls(self) -> None:
        """
        Sort the URLS contained in self.urls according to the priority given in self._source_order
        """
        sorted_urls = []
        for src_id in self._source_order:
            sorted_urls += sorted([matching_url for matching_url in self.urls if src_id in matching_url.path])
        self.urls = sorted_urls

    def _decode_function_from_target_type(self) -> Callable[[lxml.etree._Element], Any]:
        """
        This method is used to map a decode function to each target type

        Return
        ----------
        function
        """
        if "enumeration" in self._target_type:

            def to_ret(x: lxml.etree._Element) -> Any:
                return self._target_type["enumeration"][x.text]

            return to_ret
            # return lambda x, dic=self._target_type["enumeration"]: dic[x.text] #mypy did not like this

        if self._target_type["name"] == "datetime64[us]":
            return lambda x: np.datetime64(datetime.fromisoformat(x.text))  # type: ignore

        if self._target_type["name"] == "float32":
            return lambda x: np.float32(x.text)

        if self._target_type["name"] == "float64":
            return lambda x: np.float64(x.text)

        if self._target_type["name"] == "int32":
            return lambda x: np.int32(x.text)  # type: ignore

        if self._target_type["name"] == "bool":
            return lambda x: x.text in ("true", "True")

        if self._target_type["name"] == "complex64":
            return lambda x: float(x.find("re").text) + 1j * float(x.find("im").text)  # type: ignore

        if self._target_type["name"] == "|S128":
            return lambda x: x.text
        raise NotImplementedError

    def __getitem__(self, key: str) -> "EOObject":
        return self.get_data(key, target_type=self._target_type)

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        """
        This method is used to return eo_variables if parameters value match

        Parameters
        ----------
        key: str
            String containing multiple xpath expressions separated by the '#' character.
            For each source file in self._root, all the xpath expressions are executed sequentially to create
            different dimensions of the output variable.
            corresponds to a different

        Return
        ----------
        EOVariable
        """

        self._target_type = kwargs.get("target_type", self._target_type)
        self._source_order = kwargs.get("source_order", self._source_order)
        nd_xml_elem = NDimensionalXPath(self._root, key.split("#"))
        decode_function = self._decode_function_from_target_type()
        ndarray = nd_xml_elem.to_ndarray(decode_function, self._target_type["name"], self._target_type["default_value"])
        if len(ndarray.shape) == 0:
            raise KeyError(f"No values found for {key} in {self.urls}")
        return EOVariable(data=ndarray)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        nd_xml_elem = NDimensionalXPath(self._root, path.split("#"))
        if not nd_xml_elem:
            return False
        return True


@EOAccessorFactory.register_accessor("xmlsinglefile")
class XMLSingleFileAccessor(EOReadOnlyAccessor):
    """
    Single XML file accessor

    """

    _dynamic_params: list[str] = ["target_type"]

    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._root: List[lxml.etree._ElementTree] = []
        self.urls: List[AnyPath] = [p for p in self.url.glob("") if p.isfile()]
        if len(self.urls) == 0:
            raise FileNotFoundError(f"No files found in {url}")
        self._target_type: Dict[str, Any] = {}
        self._is_array = False

        self._dimension_index = None
        self._dimension_mask = None

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":

        super().open(chunk_sizes=chunk_sizes, mode=mode)

        try:
            # mandatory
            self._target_type = kwargs["target_type"]
            # optional
            self._dimension_index = kwargs.get("dimension_index")
            self._dimension_mask = kwargs.get("dimension_mask")

        except KeyError as e:
            raise MissingConfigurationParameterError(e) from e

        self._root = []
        for url in self.urls:
            with url.open() as xml_fobj:
                self._root.append(xml_utils.parse_xml(xml_fobj))

        # TODO add check
        return self

    def get_data(self, key: str, **kwargs: Any) -> "EOObject":
        """
        This method is used to return eo_variables if parameters value match.
        If both ``dimension_index`` and ``dimension_mask`` parameters are specified for the accessor,
        the variable will also be filtered along the dimension indicated by ``dimension_index``
        based on the ``dimension_mask`` criteria.

        Parameters
        ----------
        key: str
            String containing an xpath expression separated by the '#' character.

        Return
        ----------
        EOVariable
        """
        self._target_type = kwargs.get("target_type", self._target_type)
        nd_xml_elem = NDimensionalXPath(self._root, key.split("#"))
        decode_function = self._decode_function_from_target_type()
        ndarray = nd_xml_elem.to_ndarray(decode_function, self._target_type["name"], self._target_type["default_value"])
        if len(ndarray.shape) == 0:
            raise KeyError(f"No values found for {key} in {self.urls}")
        ndarray = ndarray[0]

        if self._dimension_mask:

            # filter based on local path (idx:loc), where idx represents the
            # dimension index and loc the index of the value on that dimension
            dim_idx, dim_loc = map(int, [self._dimension_index, self._dimension_mask])

            # overwrite outside filter selection with default value
            array_idx = [slice(None)] * len(ndarray.shape)
            array_idx[dim_idx] = list(range(0, dim_loc)) + list(range(dim_loc + 1, ndarray.shape[dim_idx]))
            if self._target_type["default_value"] == "NaN":
                ndarray[*array_idx] = np.nan
            else:
                ndarray[*array_idx] = self._target_type["default_value"]

        return EOVariable(data=ndarray)

    def _decode_function_from_target_type(self) -> Callable[[lxml.etree._Element], Any]:
        """
        This method is used to map a decode function to each target type

        Return
        ----------
        function
        """
        if "enumeration" in self._target_type:

            def to_ret(x: lxml.etree._Element) -> Any:
                return self._target_type["enumeration"][x.text]

            return to_ret
            # return lambda x, dic=self._target_type["enumeration"]: dic[x.text] #mypy did not like this

        if self._target_type["name"].startswith("datetime64"):
            return lambda x: np.datetime64(datetime.fromisoformat(x.text))  # type: ignore

        if self._target_type["name"] == "float32":
            return lambda x: np.float32(x.text)

        if self._target_type["name"] == "float64":
            return lambda x: np.float64(x.text)

        if self._target_type["name"] == "int32":
            return lambda x: np.int32(x.text)  # type: ignore

        if self._target_type["name"] == "bool":
            return lambda x: x.text in ("true", "True")

        if self._target_type["name"] == "complex64":
            return lambda x: float(x.find("re").text) + 1j * float(x.find("im").text)  # type: ignore

        if self._target_type["name"] == "|S128":
            return lambda x: x.text

        raise NotImplementedError

    def __getitem__(self, key: str) -> "EOObject":
        return self.get_data(key, target_type=self._target_type)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        nd_xml_elem = NDimensionalXPath(self._root, path.split("#"))
        if not nd_xml_elem:
            return False
        return True


@EOAccessorFactory.register_accessor("xml_mean_incidence_angles_s02")
class XMLMeanIncidenceAnglesAccessorS02(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract mean incidence angles arrays from S02 metadata xml
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        mean_viewing_incidence_angle_list = self.xpath(xpath)[0]
        data = []
        for mean_viewing_incidence_angle in mean_viewing_incidence_angle_list:
            band_data = []
            for angle in mean_viewing_incidence_angle.getchildren():
                band_data.append(angle.text)
            data.append(band_data)

        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(data))
        return EOVariable(data=data)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return True


@EOAccessorFactory.register_accessor("xml_mean_sun_angles_s02")
class XMLMeanSunAnglesAccessorS02(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract mean sun angles arrays from S02 MTD_TL.xml
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        xpath_result = self.xpath(xpath)
        data = np.array([elem.text for elem in xpath_result[0].getchildren()])

        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(data))
        return EOVariable(data=data)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return True


@EOAccessorFactory.register_accessor("xml_angle_names_s02")
class XMLAngleNamesAccessorS02(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract angles's names arrays from S02 xml
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        xpath_result = self.xpath(xpath)
        data = np.array([elem.tag.lower().removesuffix("_angle") for elem in xpath_result[0].getchildren()])
        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(data))
        return EOVariable(data=data)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return True


@EOAccessorFactory.register_accessor("xml_angles_s02")
class XMLAnglesAccessorS02(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract sun angles arrays from S02 xml
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """

        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        xpath_result = self.xpath(xpath)
        if len(xpath_result) == 0:
            raise KeyError(f"invalid xml xpath : {xpath} on file {self.url} {self._namespaces}")

        data = []
        for elem in xpath_result[0].getchildren():
            xml_values_list = elem.xpath("Values_List")[0]
            elem_data = self._xml_values_list_to_numpy_list(xml_values_list)
            data.append(elem_data)

        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(np.array(data)))
        return EOVariable(data=np.array(data))

    def _xml_values_list_to_numpy_list(self, values_elem: lxml.etree._Element) -> np.ndarray[Any, Any]:

        array = []
        try:
            for xml_row_of_values in values_elem.xpath("VALUES"):  # type: ignore
                row_str = xml_row_of_values.text.split(" ")  # type: ignore
                array.append(row_str)
        except Exception as err:
            raise XmlParsingError(f"Values XML list not according to specifications: {err}") from err

        return np.array(array)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return True


@EOAccessorFactory.register_accessor("xml_incidence_angles_s02")
class XMLIncidenceAnglesAccessorS02(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract incidence angles arrays from S02 xml
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        xpath_result = self.xpath(xpath)
        if len(xpath_result) == 0:
            raise KeyError(f"invalid xml xpath : {xpath} on file {self.url} {self._namespaces}")

        first_iteration = True
        data: List[Any] = []
        prev_band_id = -1
        cur_band_data: List[Any] = []
        for band_detector in xpath_result:
            detector_data = []
            for angle in band_detector.getchildren():
                angle_data = self._xml_values_list_to_numpy_list(angle.xpath("Values_List")[0])
                detector_data.append(angle_data)

            cur_band_id = band_detector.values()[0]
            if cur_band_id != prev_band_id:
                if not first_iteration:
                    data.append(cur_band_data)
                else:
                    first_iteration = False
                cur_band_data = []

            prev_band_id = cur_band_id
            cur_band_data.append(detector_data)

        data.append(cur_band_data)

        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(data))
        return EOVariable(data=data)

    @staticmethod
    def _xml_values_list_to_numpy_list(values_elem: lxml.etree._Element) -> np.ndarray[Any, Any]:

        array = []
        try:
            for xml_row_of_values in values_elem.xpath("VALUES"):  # type: ignore
                row_str = xml_row_of_values.text.split(" ")  # type: ignore
                array.append(row_str)
        except Exception as err:
            raise XmlParsingError(f"Values XML list not according to specifications: {err}") from err

        return np.array(array)

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return True


@EOAccessorFactory.register_accessor("xmlangles")
class XMLAnglesAccessor(AbstractXMLCommonOpenAccessor):
    """
    Accessor use to extract arrays from an xml file to an EOVariable.
    """

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return the eo_variables containing the xml data at xpath

        Parameters
        ----------
        key: str
            element to get in the format [formatter(]xpath such as
            "to_list(n1:Geometric_Info/Tile_Angles/Mean_Viewing_Incidence_Angle_List/.../ZENITH_ANGLE)"
        ----------
        AttributeError, it the given key doesn't match

        Return
        ----------
        EOVariable
        """
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(key)
        xpath_result = self.xpath(xpath)
        if len(xpath_result) == 0:
            raise KeyError(f"invalid xml xpath : {xpath} on file {self.url} {self._namespaces}")
        if formatter_name is not None and formatter is not None:
            return EOVariable(data=formatter.format(xpath_result))
        return EOVariable(data=self.create_eo_variable(xpath_result))

    def create_eo_variable(
        self,
        xpath_result: List[lxml.etree._Element],
    ) -> xr.DataArray:
        """
        This method is used to recover and create datasets with list values stored under
        <<VALUES>> tag.

        Example
        --------
        ::

                <Sun_Angles_Grid>
                 <Zenith>
                  <COL_STEP unit="m">5000</COL_STEP>
                  <ROW_STEP unit="m">5000</ROW_STEP>
                  <Values_List>
                    <VALUES>30.9922 30.9691 30.9461 30.9232 30.809 30.7863 30.7637 30.741</VALUES> # noqa: E501
                    ...

        """
        if len(xpath_result) == 1:
            return xml_utils.get_values_as_xr_dataarray(xpath_result[0], "/VALUES", self._namespaces)
        array_order = []
        detectors_set = set()
        bands_set = set()
        max_shape: Any = (-1, -1)
        # Recover information about each element in xpath's output (bandId, detectorId, data)
        for element in xpath_result:
            # Get bandId and detectorID from parentID (i.e azimuth / zenith)
            try:
                parent_node = element.getparent().getparent().attrib  # type: ignore
            except Exception as err:
                raise KeyError(f"Can NOT identify parent node of {element} due to: {err}") from err
            band, detector = map(int, parent_node.values())
            detectors_set.add(detector)
            bands_set.add(band)
            data = xml_utils.get_values_as_xr_dataarray(element, "/VALUES", self._namespaces)
            # Compute maximum data shape
            max_shape = max(data.shape, max_shape)
            array_order.append((band, detector, data))
        data_shape = (len(bands_set), len(detectors_set), *max_shape)
        # Create empty arrays for data
        zs = np.zeros(shape=data_shape)
        # Map data to 4d array
        detectors = sorted(list(detectors_set))
        for array_parser in array_order:
            # Fill empty data array
            row, column, data = array_parser[:3]
            zs[row][detectors.index(column)] = data
        return xr.DataArray(zs, dims=["bands", "detectors", "y_tiepoints", "x_tiepoints"])

    # docstr-coverage: inherited
    def is_group(self, path: str) -> bool:
        self.check_is_opened()  # kept for test_xml_angles_accessor
        _, _, xpath = EOFormatterFactory().get_formatter(path)
        if xpath.endswith("Values_List"):
            return False

        nodes_matched = xml_utils.flatten_str_list(self.xpath(xpath))
        if nodes_matched is not None:
            return len(nodes_matched) == 1
        return False

    # docstr-coverage: inherited
    def is_variable(self, path: str) -> bool:
        self.check_is_opened()  # kept for test_xml_angles_accessor
        _, _, xpath = EOFormatterFactory().get_formatter(path)
        if not xpath.endswith("Values_List"):
            return False

        nodes_matched = xml_utils.flatten_str_list(self.xpath(xpath))
        if nodes_matched is not None:
            return len(nodes_matched) == 1
        return False


@EOAccessorFactory.register_accessor("xmltp")
class XMLTPAccessor(AbstractXMLWithNamespacesAccessor):
    """
    Specific XML accessor to access TiePoints data in xml

    """

    def __init__(self, url: str | AnyPath, **kwargs: Any) -> None:
        super().__init__(url, **kwargs)
        self._xmltp_value: Any = {}
        self._xmltp_step: Any = {}

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """
        Parameters
        ----------
        mode: OpeningMode
        chunk_sizes : Optional[Chunk]
        kwargs: Any

        Kwargs
        -------
        Should contain at least these elements:
        - 'step_path' : step subpath to get the data stepping
        - 'values_path' : subpath to get the actual values
        - 'namespaces' : namespaces to apply to the xml etree
        """
        mode = OpeningMode.cast(mode)
        if mode == OpeningMode.OPEN:
            try:
                self._xmltp_step = kwargs["step_path"]  # replace Any with actual type (typing issue)
                self._xmltp_value = kwargs["values_path"]
                self._namespaces = kwargs["namespace"]
            except KeyError as e:
                raise MissingArgumentError(f"Missing configuration parameter: {e}") from e
            if not self.url.isfile():
                raise FileNotFoundError(f"Can't find file {self.url}")
            with self.url.open() as xml_fobj:
                self._root = xml_utils.parse_xml(xml_fobj)
            super().open(chunk_sizes=chunk_sizes, mode=mode)
        return self

    def _get_shape(self, xpath: str) -> list[int]:
        """
        This method is used to recover array shape from a given xpath node
        Parameters
        ----------
        xpath: str
            path to dimensions node

        Return
        ----------
        list(int):
            List with dimensions
        """
        list_ = self.xpath(xpath)
        return [len(list_), len(list_[0].text.split())]

    def _get_tie_points_data(self, path: str) -> xr.DataArray:
        shape_y_x = self._get_shape(self._xmltp_value)
        resolution = float(self.xpath(path)[0].text)
        step = float(self.xpath(self._xmltp_step)[0].text)
        if path[-1] == "Y":
            data = [resolution - i * step for i in range(shape_y_x[0])]
        elif path[-1] == "X":
            data = [resolution + i * step for i in range(shape_y_x[1])]
        else:
            raise AttributeError("Invalid dimension")
        return xr.DataArray(data)

    def __getitem__(self, key: str) -> "EOObject":
        """
        This method is used to return eo_variables filled with the tiepoints data

        Parameters
        ----------
        key: str
            variable xpath

        Return
        ----------
        EOVariable, if the given key match

        Raise
        ----------
        AttributeError, it the given key doesn't match
        """

        xpath_results: List[lxml.etree._Element] = self.xpath(key)
        if xpath_results is None or not xpath_results:
            raise KeyError(f"Incorrect xpath {key}")

        return EOVariable(name=key, data=self._get_tie_points_data(key))

    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        # xmlTP accessor only returns variables
        return False

    def is_variable(self, path: str) -> bool:
        """
        I guess if the len of the flatten values is 1 then it means it is a variable ('X','Y') etc
        """
        filtered: Optional[str] = xml_utils.flatten_str_list(self.xpath(path))
        if filtered is not None:
            return len(filtered) == 1
        return False


@EOAccessorFactory.register_accessor("xmlmetadata")
class XMLManifestAccessor(EOAccessor):
    """
    Accessor to handle xml files to extract a list of xpath to corresponding eoproduct attribute.
    Mapping is provided in dict like this ::

            "stac_discovery": {
                    "type": "Text(Feature)",
                    "stac_version": "Text(1.0.0)",
                    "stac_extensions": [
                        "Text(https://stac-extensions.github.io/eopf/v1.0.0/schema.json)",
                        "Text(https://stac-extensions.github.io/eo/v1.1.0/schema.json)",
                        "Text(https://stac-extensions.github.io/sat/v1.0.0/schema.json)",
                        "Text(https://stac-extensions.github.io/view/v1.0.0/schema.json)",
                        "Text(https://stac-extensions.github.io/scientific/v1.0.0/schema.json)",
                        "Text(https://stac-extensions.github.io/processing/v1.1.0/schema.json)"
                    ],
                    "id": "n1:General_Info/Product_Info/PRODUCT_URI",
                    "geometry": "to_geoJson(metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap...
                    "bbox": "to_bbox(metadataSection/metadataObject[@ID='measurementFrameSet']/metadataWrap/xmlData...
                    "properties": {
                        "datetime": "to_datetime(n1:General_Info/Product_Info/*[contains(local-name(), '_TIME')])",
                        "start_datetime": "n1:General_Info/Product_Info/PRODUCT_START_TIME",
                        "end_datetime": "n1:General_Info/Product_Info/PRODUCT_STOP_TIME",
                        "created": "n1:General_Info/Product_Info/GENERATION_TIME",
                        "platform": "to_str_lower(n1:General_Info/Product_Info/Datatake/SPACECRAFT_NAME)",
                        "instrument": "Text(msi)",
                        "mission": "Text(Sentinel-2)",
                        ....


    """

    KEYS = ["CF", "OM_EOP"]
    _dynamic_params = ["path_template", "namespaces"]

    def __init__(self, url: str | AnyPath, *args: Any, **kwargs: Any) -> None:
        super().__init__(url, *args, **kwargs)
        self._namespaces: dict[str, str] = {}
        self._metadata_mapping: Optional[MutableMapping[str, Any]] = None
        self.url = self.url.glob("")[0] if self.url.glob("") else self.url
        self._attrs: MutableMapping[str, Any] = {}
        self._parsed_xml: Optional[lxml.etree._ElementTree] = None
        self._product_name = str()
        self._pattern_writer: Optional[PatternWriter] = None
        self.LOGGER = EOLogging().get_logger(name="eopf.accessor.xml_accessor")

    def open(
        self,
        mode: OpeningMode | str = OpeningMode.OPEN,
        chunk_sizes: Optional[Chunk] = None,
        **kwargs: Any,
    ) -> "EOAccessor":
        """Open the xml file and apply the mapping to get the attribute dict

        Parameters
        ----------
        chunk_sizes
        mode: str, optional
            unused
        **kwargs: Any
            extra kwargs through which configuration parameters are passed
            'path_template' dict containing 'template_folder' and 'template_name' to be provided in writing mode
            'mapping' : dict of data mapping with attrs_name:[formatter]xpath format
        """
        self.LOGGER.debug(f"Opening file {self.url}")
        mode = OpeningMode.cast(mode)
        if mode in [OpeningMode.CREATE, OpeningMode.CREATE_OVERWRITE, OpeningMode.UPDATE, OpeningMode.APPEND]:
            try:
                pattern_infos = kwargs["path_template"]
            except KeyError as e:
                raise TypeError(f"Missing configuration parameter : {e}") from e
            self._pattern_writer = PatternWriter.sync_writer(
                self.url,
                pattern_infos["template_folder"],
                pattern_infos["template_name"],
            )
            super().open(mode=mode, chunk_sizes=chunk_sizes)
            return self
        if mode != OpeningMode.OPEN:
            raise NotImplementedError()
        # get configuration parameters
        try:
            self._metadata_mapping = kwargs["mapping"]
            self._namespaces = kwargs["namespaces"]
        except KeyError as e:
            raise MissingArgumentError(f"Missing configuration parameter: {e}") from e

        # open the manifest xml
        super().open(mode=mode)
        if not self.url.isfile():
            raise FileNotFoundError(f"Can't find file at {self.url}")
        return self

    def close(self) -> None:
        super().close()
        if self._pattern_writer is not None:
            self._pattern_writer.close()
        self._pattern_writer = None

    def __getitem__(self, key: str) -> "EOObject":
        """Getter for CF and OM_EOP attributes of the xml into EOProduct attributes

        Parameters
        ----------
        key: str, optional
            unused as it will take the mapping param

        Returns
        ----------
        The CF an OM_EOP dictionary as attributes of a EOGroup: MutableMapping[str, Any]:
        """
        self.check_is_opened()

        if self._parsed_xml is None:
            self._parse_xml()

        # create an EOGroup and register_requested_parameter its attributes with a dictionary containing CF and OM_EOP
        if self._metadata_mapping is not None:
            self._attrs = self._translate_attributes(self._metadata_mapping)
        else:
            # Todo provide short_name somewhere
            self._attrs = {}

        eog: EOGroup = EOGroup("product_metadata", attrs=self._attrs)
        return eog

    def _parse_dict_value(self, key: str, value: Any, internal_dict: Dict[str, Any]) -> Any:
        rex = r".*\((.*)\)"
        match = re.match(rex, value)
        if match:
            # the xpath is wrapped by a formatter function
            stac_conversion = self.stac_mapper(value)
            if stac_conversion is not None:
                internal_dict[key] = stac_conversion
            else:
                # the xpath is not valid, a warning may be raised
                # however, to allow reading fields from various xmls, as in the case of S2
                # we do not raise any warning or error
                self.LOGGER.debug(f"Invalid xpath/command : {value} on file {self.url}")
        else:
            try:
                if self._parsed_xml is None:
                    xpath_result = None
                else:
                    xpath_result = xml_utils.get_xpath_results(self._parsed_xml, value, self._namespaces)
                if xpath_result is None:
                    raise XmlXpathError(f"No result for {value} in {self.url}")
                if isinstance(xpath_result, list) and len(xpath_result) == 0:
                    raise XmlXpathError(f"No result for {value} in {self.url}")
                if isinstance(xpath_result, list):
                    str_list = xml_utils.element_to_str_list(xpath_result)
                    # if a single element return it directly
                    internal_dict[key] = str_list[0] if len(str_list) == 1 else str_list
                else:
                    internal_dict[key] = None
            except XmlXpathError:
                # the xpath is not valid, a warning may be raised
                # however, to allow reading fields from various xmls, as in the case of S2
                # we do not raise any warning or error
                # might need some refactor at some points
                self.LOGGER.debug(f"Invalid xpath/command : {value} on file {self.url}")

    def _parse_id_keys(self, key: str, value: Any) -> None:
        try:
            if self._parsed_xml is None:
                xpath_result: Optional[List[lxml.etree._Element]] = None
            else:
                xpath_result = xml_utils.get_xpath_results(
                    self._parsed_xml,
                    value,
                    self._namespaces,
                )
            if xpath_result is None:
                raise XmlXpathError(f"No result for {value} in {self.url}")
            if (
                isinstance(xpath_result, list)
                and len(xpath_result) == 1
                and xpath_result[0] is not None
                and xpath_result[0].text is not None
            ):
                self._product_name = xpath_result[0].text
            else:
                raise XmlXpathError("id element should be a single value")

        except XmlXpathError:
            # the xpath is not valid, a warning may be raised
            # however, to allow reading fields from various xmls, as in the case of S2
            # we do not raise any warning or error
            self.LOGGER.debug(f"Invalid xpath/command : {key} {value} on file {self.url}")

    def _translate_dict_attributes(self, attributes_dict: Dict[str, Any]) -> Any:

        internal_dict = dict()
        for key, value in attributes_dict.items():
            if key == "id":
                self._parse_id_keys(key, value)

            # Recursive call for nested dictionaries
            if isinstance(value, dict):
                internal_dict[key] = self._translate_attributes(value)
                continue

            # Skip non-string formatted elements (list)
            if isinstance(value, list):
                internal_dict[key] = self._translate_list_attributes(value, key)
                continue

            if isinstance(value, str) and ".nc:" in value:
                # these attrs are treated by NcToAttr accessor, see netcdf accessors
                continue

            if isinstance(value, str) and ".dat:" in value:
                # these attrs are treated by DatToAttr accessor, see memmap accessors
                continue

            self._parse_dict_value(key, value, internal_dict)

        return internal_dict

    def _translate_attributes(self, attributes_dict: MutableMapping[str, Any], stac_mapper_only: bool = False) -> Any:
        """Used to convert values from metadata mapping

        Parameters
        ----------
        attributes_dict: dict
            dictionary containing metadata
        stac_only: bool
            Alays apply stac_mapper, don't test for formatter regex

        Returns
        ----------
        internal_dict: dict
            dictionary containing converted values (using get_xpath_results or conversion functions)
        """
        # This function is used to parse an convert each value from attributes dictionary
        internal_dict = dict()
        if self._parsed_xml is None:
            raise AttributeError("Document should be parsed")
        if isinstance(attributes_dict, str):
            # introduced for ToProcessingHistoryS03 and ToProcessingHistoryS01
            internal_dict = self.stac_mapper(attributes_dict)
        elif isinstance(attributes_dict, dict):
            internal_dict = self._translate_dict_attributes(attributes_dict)

        return internal_dict

    def _translate_list_attributes(
        self,
        attributes_list: Union[List[Any], Dict[Any, Any]],
        global_key: Optional[str] = None,
    ) -> Any:
        """Used to convert values from metadata mapping

        Parameters
        ----------
        attributes_list: list
            list containing metadata

        Returns
        ----------
        local_list_of_dicts: List[dict]
            A list of dictionaries containing converted values in the same nesting as input list.
        """
        local_list_of_dicts = []
        # Iterate through input list
        for idx in attributes_list:
            self.LOGGER.debug(f"Treating {idx}")
            local_dict = {}
            if isinstance(idx, str):
                converted_value = self.stac_mapper(idx)
                if converted_value is not None:
                    local_list_of_dicts.append(converted_value)
                else:
                    local_list_of_dicts.append(idx)
                continue
            if isinstance(idx, list):
                # Recursive call for nested lists
                # TODO : big code smell in here, nothing is done with this result
                local_dict[global_key] = self._translate_list_attributes(idx)
                continue
            if isinstance(idx, dict):
                local_dict = self._translate_attributes(idx, stac_mapper_only=True)

            if local_dict:
                local_list_of_dicts.append(local_dict)
        return local_list_of_dicts

    def _get_single_xml_raw_data(self, xpath: str) -> Any:
        if self._parsed_xml is not None:
            return xml_utils.get_first_xpath_result(self._parsed_xml, xpath, namespaces=self._namespaces)
        return None

    def _get_single_xml_data(self, xpath: str) -> Any:
        """Used to get data from xml file

        Parameters
        ----------
        xpath: str
            xpath

        Returns
        ----------
        Any
            xml acquired data
        """
        xml_data = self._get_single_xml_raw_data(xpath)
        return xml_utils.get_text(xml_data)

    def _get_xml_raw_data(self, xpath: str) -> Any:
        if self._parsed_xml is not None:
            return xml_utils.get_xpath_results(self._parsed_xml, xpath, namespaces=self._namespaces)
        return None

    def _get_xml_data(self, xpath: str) -> Any:
        """Used to get data from xml file

        Parameters
        ----------
        xpath: str
            xpath

        Returns
        ----------
        Any
            xml acquired data
        """
        xml_data = self._get_xml_raw_data(xpath)
        return xml_utils.get_text(xml_data)

    def _get_nc_data(self, path_and_dims: str) -> Any:
        """Used to get data from netCDF file

        Parameters
        ----------
        path_and_dims: str
            a path to a netCDF file followed by requested dims

        Returns
        ----------
        Any
            netCDF acquired data
        """

        # parse the input string for relative file path
        # and wanted dims, perform checks on them
        rel_file_path, wanted_dims = path_and_dims.split(":")
        file_path = self.url.dirname() / rel_file_path
        if not file_path.isfile():
            raise XmlManifestNetCDFError(f"NetCDF file {file_path} does NOT exist")
        if len(wanted_dims) < 1:
            raise XmlManifestNetCDFError("No dimensions are required")

        # create a dict with the requested dims
        ret_dict: Dict[str, Union[None, int]] = {w: None for w in wanted_dims.split(",")}

        # open netcdf file and read the dims and shape of fist var
        try:
            ncs = EONetCDFAccessor(file_path)
            ncs.open()
            var = ncs[list(ncs.iter("/"))[0]]
            if isinstance(var, EOVariable):
                var_dims = var.dims
                var_shp = var.data.shape
            else:
                # practically not possible
                raise XmlManifestNetCDFError(f"Expected EOVariable not {type(var)}")
        finally:
            ncs.close()

        # iter over the the val dims and populate the requested dims
        for idx, val in enumerate(var_dims):
            if val in ret_dict.keys():
                ret_dict[val] = var_shp[idx]

        # check if all requested dims were populated
        for k in ret_dict.keys():
            if ret_dict[k] is None:
                raise XmlManifestNetCDFError(f"Dim {k} not found")

        return ret_dict

    def stac_mapper(self, path: str) -> Any:  # xenon: noqa
        """Used to handle xpath's that request a conversion

        Parameters
        ----------
        path: str
            xpath which may contain formatters

        Returns
        ----------
        Any:
            output of the data getters either xml, netCDF
        """

        # parse the path
        formatter_name, formatter, xpath = EOFormatterFactory().get_formatter(path)

        try:
            # If formatter is not defined, just read xpath and return data
            if formatter_name is None or formatter is None:
                return self._get_single_xml_data(xpath)
            elif formatter_name in [ToProcessingHistoryS03.name, ToProcessingHistoryS01.name]:
                return formatter.format(
                    (
                        self._get_single_xml_raw_data(xpath),
                        self._namespaces,
                    ),
                )
            elif formatter_name == ToImageSize.name:
                return formatter.format(self._get_nc_data(xpath))
            elif formatter_name == ToS02Adfs.name:
                xml_node = self._get_single_xml_raw_data("n1:Auxiliary_Data_Info")
                if isinstance(xml_node, lxml.etree._Element):
                    return formatter.format((xml_node, xpath))
                else:
                    return list()
            if self._parsed_xml is not None:
                return formatter.format_stac_mapper(self._parsed_xml, xpath, self._namespaces)
        except Exception as e:
            self.LOGGER.debug(f"Invalid xpath {xpath} : {e}")
            return None

    def _parse_xml(self) -> None:
        """Parses the manifest xml and saves it in _parsed_xml

        Raises
        ----------
        AccessorNotOpenError
            Trying to parse an xml that was not opened
        XmlParsingError
            Any error while parsing the xml
        """
        self.check_is_opened()

        with self.url.open() as xml_fobj:
            try:
                self._parsed_xml = xml_utils.parse_xml(xml_fobj)
            except Exception as e:
                raise XmlParsingError(f"Exception while computing xfdu dom: {e}") from e

    def __setitem__(self, key: str, value: "EOObject") -> None:
        self.write_attrs(key, value.attrs)

    def is_group(self, path: str) -> bool:
        self.check_is_opened()
        return True

    def is_variable(self, path: str) -> bool:
        self.check_is_opened()
        return False

    def write_attrs(self, group_path: str, attrs: Optional[MutableMapping[str, Any]] = None) -> None:
        self.check_is_opened()
        not_none(self._pattern_writer)[group_path] = attrs


class PatternWriter:
    """Class writing a file according to a jinja pattern.
    Prefer using the sync_writer factory to create this class as it manage
    multiple instance of this class writing the same file.

    """

    _singleton_by_url: WeakValueDictionary[AnyPath, "PatternWriter"] = WeakValueDictionary()

    def __init__(self, url: AnyPath, templates_path: str, template_name: str):
        env = Environment(loader=FileSystemLoader(templates_path), autoescape=True)
        self._template = env.get_template(template_name)
        self._url = url
        self._context_data: dict[str, dict[str, Any]] = {}  # dict of attributes by group path
        self._ref_count: int = 1

    def __del__(self) -> None:
        if self._ref_count != 0:
            self._ref_count = 0
            self._write()

    def __setitem__(self, key: str, value: Any) -> None:
        if key in ["", "/"]:
            key = "PRODUCT"
        self._context_data[key] = value
        # no need to fuse, we cna have multiple time the same key but then value will be the same object.

    def close(self) -> None:
        self._ref_count -= 1
        if self._ref_count == 0:
            self._write()

    def _write(self) -> None:
        """Write the file. Automatically called when all writers on an url are closed or deleted."""
        output = self._template.render(self._context_data)

        with self._url.open(mode="w") as f:
            f.write(output)

    @classmethod
    def sync_writer(
        cls: type["PatternWriter"],
        url: AnyPath,
        templates_path: str,
        template_name: str,
    ) -> "PatternWriter":
        """
        Factory of PatternWriter. Return one PatternWriter by url, and allow opening/closing counting.
        Writing different patterns on one url is not supported.

        Parameters
        ----------
        url: AnyPath
            url of the written file
        templates_path: str
            path to the pattenr folder
        template_name: str
            name of the pattern file used (in the pattern folder)

        Returns
        -------
        PatternWriter of url according to templates_path/template_name
        """

        # Only one when multiple accessor try to write in the same file.
        new_obj: PatternWriter
        if url not in cls._singleton_by_url:
            new_obj = PatternWriter(url, templates_path, template_name)
            cls._singleton_by_url[url] = new_obj
        else:
            new_obj = cls._singleton_by_url[url]
            new_obj._ref_count += 1
        # we need to know when all Accessors using this Writter are closed.
        # not sure why relying on GC ref count + weakref fail.
        return new_obj


class NDimensionalXPath:
    """Representation of an N-dimensional data structure containing XML elements.
    These elements are derived applying multiple xpath expressions on multiple XML files having the same structure.

    Parameters
    ----------
    xml_etree_roots: list[lxml.etree._ElementTree]
        list of XML roots
    xpath_list: list[str]
        list of xpath strings to be applied on each XML tree root
    """

    def __init__(self, xml_etree_roots: List[lxml.etree._ElementTree], xpath_list: List[str]):
        self._list = self._recursive_xpath(xml_etree_roots, xpath_list)
        self._expand_array_nodes()
        self._gen: Iterator[Tuple[Any, lxml.etree._ElementTree]] = iter(())

    def _recursive_xpath(
        self,
        elem_list: List[lxml.etree._ElementTree],
        xpath_list: List[str],
    ) -> List[lxml.etree._ElementTree]:
        """Recursively apply a list of xpaths on a list of XML elements.

        Parameters
        ----------
        elem_list: list[lxml.etree._ElementTree]
            list of XML elements
        xpath_list: list[str]
            list of xpath strings to be applied on each XML element

        Return
        ----------
        list[lxml.etree._ElementTree]
        """

        if len(xpath_list) == 1:
            # return [elem.xpath(xpath_list[0]) for elem in elem_list]
            return [
                extracted[0] if len(extracted := elem.xpath(xpath_list[0])) == 1 else extracted  # type: ignore # noqa
                for elem in elem_list
            ]
        return [
            self._recursive_xpath(elem.xpath(xpath_list[0]), xpath_list[1:])  # type: ignore # noqa
            for elem in elem_list
        ]

    def _expand_array_nodes(self, sep: Optional[str] = None) -> None:
        """Expand each XML element having a 'count' attribute to a list of values.

        Parameters
        ----------
        sep: str, optional
            Separator used to expand the textual content of each XML element
        """
        for idx, elem in self.enumerate():
            if "count" in elem.attrib:  # type: ignore
                split_array = elem.text.split(sep)  # type: ignore
                self[idx] = []  # type: ignore
                for value in split_array:
                    new_el = lxml.etree.Element(elem.tag)  # type: ignore
                    new_el.text = value
                    self[idx].append(new_el)  # type: ignore

    def __getitem__(self, key: Sequence[int]) -> lxml.etree._ElementTree:
        to_ret = self._list[key[0]]
        for idx in key[1:]:
            to_ret = to_ret[idx]  # type: ignore
        return to_ret

    def __setitem__(self, key: Sequence[int], value: lxml.etree._ElementTree) -> None:
        last_list = self._list
        while len(key) > 1:
            last_list = last_list[key[0]]  # type: ignore
            key = key[1:]
        last_list[key[0]] = value

    def __iter__(self) -> Iterator[Tuple[Any, lxml.etree._ElementTree]]:
        self._gen = self.enumerate()
        return self  # type: ignore

    def __next__(self) -> lxml.etree._ElementTree:
        next_idx, next_val = next(self._gen)
        return next_val

    def __len__(self) -> int:
        num_elems = 0
        for v in self:
            num_elems += 1
        return num_elems

    def enumerate(self) -> Iterator[Tuple[Any, lxml.etree._ElementTree]]:
        """Generator yielding tuples in the form (index, value), where index is a tuple that can be used as an index,
        and value is an XML Element.

        Yields
        ----------
        (index, lxml.Element)
        """
        yield from self._enumerate(self._list, None)

    @staticmethod
    def _enumerate(lst: Any, index: Any) -> Iterator[Tuple[Any, lxml.etree._ElementTree]]:
        if isinstance(lst, lxml.etree._Element):  # pylint: disable=protected-access
            yield (index,), lst
        else:
            for my_index, my_value in enumerate(lst):
                for sub_index, sub_value in NDimensionalXPath._enumerate(my_value, my_index):
                    if index is None:
                        yield sub_index, sub_value
                    else:
                        yield (index, *sub_index), sub_value

    def get_ndarray_shape(self) -> List[int]:
        """Compute the shape of the N-dimensional array obtained from a list-of-list of depth N containing XML elements.
        Also computes the amount of padding necessary in each dimension so that the N-dimensional array
        is not ragged.

        Return
        ----------
        list[int]
        """
        if len(self) == 0:
            return []
        return self._get_ndarray_shape(self._list)

    @staticmethod
    def _get_ndarray_shape(lst: Any) -> List[int]:
        """Compute the shape of the N-dimensional array obtained from a list-of-list of depth N containing XML elements.
        The function computes also the amount of padding necessary in each dimension so that the N-dimensional array
        is not ragged.
        Attention: the function assumes the tree representing the list-of-list is balanced, i.e. evey node has the same
        depth.

        Parameters
        ----------
        lst: list
            list of lists of depth N corresponding to an N-dimensional array
        Return
        ----------
        list[int]
        """
        if isinstance(lst, lxml.etree._Element):  # pylint: disable=protected-access
            return []

        max_sublist_shape = NDimensionalXPath._get_ndarray_shape(lst[0])
        if not max_sublist_shape:
            return [len(lst)]

        for list_elem in lst[1:]:
            sublist_shape = NDimensionalXPath._get_ndarray_shape(list_elem)
            max_sublist_shape = [max(a, b) for a, b in zip(max_sublist_shape, sublist_shape)]
        return [len(lst), *max_sublist_shape]

    def to_ndarray(
        self,
        decode_function: Callable[[lxml.etree._Element], Any],
        type_str: str,
        default_value: Any,
    ) -> np.typing.NDArray[Any]:
        """Creates a Numpy ndarray representation of the N-dimensional structure of XML elements generated by the xpath

        Parameters
        ----------
        decode_function: function
            function used to decode the xpath elements
        type_str: str
            string representation of the type of the output ndarray
        default_value: Any
            default value of the output ndarray. This is used only in case padding is necessary.
        Return
        ----------
        numpy.ndarray
        """
        shape = self.get_ndarray_shape()
        array = np.full(shape, default_value, dtype=type_str)
        for index, value in self.enumerate():
            array_index = np.pad(index, (0, len(shape) - len(index)))
            array[tuple(array_index)] = decode_function(value)  # type: ignore
        return array
