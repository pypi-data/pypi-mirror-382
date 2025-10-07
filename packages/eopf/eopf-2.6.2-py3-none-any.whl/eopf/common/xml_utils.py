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
xml_utils.py

xml utils to access data in xml to centralize all the xml calls

"""
from io import TextIOWrapper
from typing import Any, Dict, List, Optional, TextIO, Union, overload

import xarray as xr
from lxml import etree
from lxml.etree import _ElementUnicodeResult

from eopf.exceptions.errors import XmlXpathError


@overload
def parse_xml(_arg1: TextIOWrapper) -> Any: ...


@overload
def parse_xml(_arg1: TextIO) -> Any: ...


@overload
def parse_xml(_arg1: str) -> Any: ...


def parse_xml(path: str) -> Any:
    """Parse an XML file and create an object

    Parameters
    ----------
    path: str
        Path to the directory of the product
    Returns
    -------
    Any
        ElementTree object loaded with source elements :
    """
    return etree.parse(path)


def get_namespaces(dom: Any) -> Dict[str, str]:
    """
    Get the namespaces listed in th dom etree
    Parameters
    ----------
    dom

    Returns
    -------

    """
    namespaces = {}
    # Use iterparse to collect namespaces
    for _, elem in etree.iterparse(dom, events=("start-ns",)):
        prefix, uri = elem
        namespaces[prefix] = uri
    return namespaces


# Redefine it here to fix AttributeError: module 'lxml.etree' has no attribute '_ElementOrTree'
_ElementOrTree = Union[etree._Element, etree._ElementTree]


def get_xpath_results(dom: _ElementOrTree, xpath: str, namespaces: dict[str, str]) -> Any:
    """Apply the XPath on the DOM

    Parameters
    ----------
    dom : Any
        The DOM to be parsed with xpath
    xpath : str
        The value of the corresponding XPath rule
    namespaces : dict
        The associated namespaces

    Returns
    -------
    str
        The result of the XPath

    Raises
    ------
        KeyError: invalid xpath
    """
    try:
        return dom.xpath(xpath, namespaces=namespaces)
    except etree.XPathEvalError as exc:
        raise XmlXpathError("Invalid path " + xpath) from exc


def get_first_xpath_result(dom: Any, xpath: str, namespaces: dict[str, str]) -> Any:
    """Apply the XPath on the DOM

    Parameters
    ----------
    dom : Any
        The DOM to be parsed with xpath
    xpath : str
        The value of the corresponding XPath rule
    namespaces : dict
        The associated namespaces

    Returns
    -------
    str
        The result of the XPath

    Raises
    ------
        KeyError: invalid xpath
    """
    ret = get_xpath_results(dom, xpath, namespaces=namespaces)
    if isinstance(ret, list):
        if len(ret) > 0:
            return ret[0]
        raise XmlXpathError(f"No element found for {xpath} in file")
    return ret


def get_text(xml_data: Any) -> Optional[Union[List[str], str]]:
    """
    Get the text of the xml node
    None if this is not a text node

    Parameters
    ----------
    xml_data

    Returns
    -------

    """
    if isinstance(xml_data, list):
        return [get_text(f) for f in xml_data]
    if isinstance(xml_data, _ElementUnicodeResult):
        # Convert ElementUnicodeResult to string
        return str(xml_data)
    if hasattr(xml_data, "text"):
        if xml_data.text is None:
            # Case where data is stored as attribute eg: <olci:invalidPixels value="749556" percentage="4.000000"/>
            return xml_data.values()[0]
        # Nominal case, eg: <olci:alTimeSampling>44001</olci:alTimeSampling>
        return xml_data.text
    return None


def flatten_str_list(xpath_result: list[etree._Element]) -> Optional[str]:
    """
    Use to flatten all elements into a single str using , join

    Parameters
    ----------
    xpath_result

    Returns

    """
    if not isinstance(xpath_result, list):
        raise TypeError("Only list accepted")
    if len(xpath_result) >= 1:
        if isinstance(xpath_result[0], etree._Element):
            if len(xpath_result) == 1:
                if xpath_result[0].text is not None:
                    return xpath_result[0].text
                else:
                    ret = ""
                    for val in xpath_result[0].values():
                        ret = ret + " " + str(val)
                    return ret[1:]
            else:
                return ",".join([elt.text for elt in xpath_result])

        if isinstance(xpath_result[0], etree._ElementUnicodeResult):
            # When accessing xml attributes (with @), the object returned is a list with the attribute
            # as an ElementUnicodeResult. We retrieve it and cast it to str.
            return ",".join([str(elt) for elt in xpath_result])

    return ""


def element_to_str_list(xpath_result: list[etree._Element]) -> list[str]:
    """
    Transform a list of etree element to list of str
    Parameters
    ----------
    xpath_result

    Returns
    -------
    list[str]
    """

    if not isinstance(xpath_result, list):
        raise TypeError("Only list accepted")

    if isinstance(xpath_result[0], etree._Element):
        return [elt.text for elt in xpath_result]

    if isinstance(xpath_result[0], etree._ElementUnicodeResult):
        # When accessing xml attributes (with @), the object returned is a list with the attribute
        # as an ElementUnicodeResult. We retrieve it and cast it to str.
        return [str(elt) for elt in xpath_result]

    return []


def get_values_as_xr_dataarray(dom: Any, xpath: str, namespaces: dict[str, str]) -> xr.DataArray:
    """
    This method is used to convert data from a xml node to a xarray dataarray

    It is searching for /VALUES list in the sub xpath

    Parameters
    -------
    dom: eteee._Element
    xpath: str xpath
    namespaces: namespaces of xml

    Returns
    -------
    xr.DataArray
    """
    # TODO : why xpath params is not used ?
    reenlist = dom.xpath("VALUES", namespaces=namespaces)
    # Convert every value from xml to a floating point representation
    array = [[float(i) for i in x.text.split()] for x in reenlist]
    # Create 2d DataArray
    da = xr.DataArray(array, dims=["y_tiepoints", "x_tiepoints"])
    return da


def xml_local_name(element: etree._Element) -> str:
    """Retrieve localname, the tag name, without the namespace URI."""
    return etree.QName(element).localname
