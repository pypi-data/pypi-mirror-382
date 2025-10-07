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
xml_formatters.py

WML data formatters

"""
from re import match
from typing import Any, Dict, List, Optional, Tuple

import lxml.etree
import numpy

from eopf.common import date_utils, history_utils, xml_utils
from eopf.common.constants import (
    PROCESSING_HISTORY_ADFS_FIELD,
    PROCESSING_HISTORY_FACILITY_FIELD,
    PROCESSING_HISTORY_INPUTS_FIELD,
    PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN,
    PROCESSING_HISTORY_OUTPUTS_FIELD,
    PROCESSING_HISTORY_PROCESSOR_FIELD,
    PROCESSING_HISTORY_TIME_FIELD,
    PROCESSING_HISTORY_UNKNOWN_MARKER,
    PROCESSING_HISTORY_UNKNOWN_TIME_MARKER,
    PROCESSING_HISTORY_VERSION_FIELD,
)
from eopf.exceptions import FormattingError

from .abstract import (
    EOAbstractGenericXMLFormatter,
    EOAbstractListValuesFormatter,
    EOAbstractSingleValueFormatter,
    EOAbstractXMLFormatter,
)


class ToDatetime(EOAbstractXMLFormatter):
    """Formatter for the datetime attribute compliant with the stac standard"""

    # docstr-coverage: inherited
    name = "to_datetime"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> Optional[str]:
        """
        The datetime retrived from the product from XML search, the datetime STAC attribute
        should contain the middle time between the start_datetime and the end_datetime.

        Return the time formatted according to ISO with the UTC offset attached,
        giving a full format of 'YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM'.
        The fractional part is omitted if self.microsecond == 0.
        """
        # map children content (text value) to tag names without namespace URIs
        children = {xml_utils.xml_local_name(elt): elt.text for elt in xpath_input}
        candidates = [
            ["startTime", "stopTime"],  # S01 & S03 tag
            ["PRODUCT_START_TIME", "PRODUCT_STOP_TIME"],  # S02 tag (Product_Info)
            ["DATASTRIP_SENSING_START", "DATASTRIP_SENSING_STOP"],  # S02 tag (Datastrip_Time_Info)
        ]
        for tag_start, tag_stop in candidates:
            if tag_start in children and tag_stop in children:
                start = children[tag_start]
                stop = children[tag_stop]
                if start is not None and stop is not None and len(start) > 1 and len(stop) > 1:
                    return date_utils.stac_iso8601(
                        date_utils.middle_date(date_utils.force_utc_iso8601(start), date_utils.force_utc_iso8601(stop)),
                    )
                self._logger.warning("datetime: empty text, can not compute middle time")
        self._logger.warning("datetime: tag not found, can not compute middle time")
        return None


class ToBands(EOAbstractXMLFormatter):
    """
    Format to list of bands
    """

    name = "to_bands"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> List[str]:
        bands_set = set()
        for element in xpath_input:
            band_id = str(element.attrib["bandId"])
            if len(band_id) == 1:
                bands_set.add(f"b0{band_id}")
            else:
                bands_set.add(f"b{band_id}")

        return sorted(bands_set)


class ToPosList(EOAbstractXMLFormatter):
    """Formatter for the pos list to a single str"""

    # docstr-coverage: inherited
    name = "to_pos_list"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> Optional[str]:
        """
        Use to filter the posList element to provide a specific formatting for them

        Parameters
        ----------
        xpath_input

        Returns
        ---------
        Pos list formatted to string

        """
        if not isinstance(xpath_input, list):
            raise TypeError("Only list accepted")
        if len(xpath_input) == 0:
            return None

        if isinstance(xpath_input[0], lxml.etree._Element):
            if len(xpath_input) == 1:
                return self._format_single_element(xpath_input[0])
            return ",".join([elt.text for elt in xpath_input])

        if isinstance(xpath_input[0], lxml.etree._ElementUnicodeResult):
            # When accessing xml attributes (with @), the object returned is a list with the attribute
            # as an ElementUnicodeResult. We retrieve it and cast it to str.
            return str(xpath_input[0])

        return None

    @staticmethod
    def _format_single_element(xpath_input: lxml.etree._Element) -> str:
        """
        When the pos list is in a single xml tag

        Parameters
        ----------
        xpath_input

        Returns
        -------

        """

        if xpath_input.tag.endswith("posList") and xpath_input.text is not None:
            values = xpath_input.text.split(" ")
            match_list = ", ".join(" ".join([values[idx + 1], values[idx]]) for idx in range(0, len(values) - 1, 2))
            return f"POLYGON(({match_list}))"
        if xpath_input.text is not None:
            return xpath_input.text
        ret = ""
        for val in xpath_input.values():
            ret = ret + " " + str(val)
        return ret[1:]


class ToDetectors(EOAbstractXMLFormatter):
    """
    Format the xml list of detectors
    """

    name = "to_detectors"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> List[str]:
        detectors_set = set()
        for element in xpath_input:
            detector_id = str(element.attrib["detectorId"])
            if len(detector_id) == 1:
                detectors_set.add(f"d0{detector_id}")
            else:
                detectors_set.add(f"d{detector_id}")

        return sorted(detectors_set)


class ToMean(EOAbstractListValuesFormatter):
    """
    Compute the mean
    """

    name = "to_mean"

    def _format(self, xpath_input: List[str]) -> Any:
        return numpy.mean([float(element) for element in xpath_input])


class ToList(EOAbstractListValuesFormatter):
    """
    Format to list of values
    """

    name = "to_list"

    def _format(self, xpath_input: List[str]) -> Any:
        return [float(element) for element in xpath_input]


class ToListStr(EOAbstractListValuesFormatter):
    """
    Format to list of str values
    """

    name = "to_list_str"

    def _format(self, xpath_input: List[str]) -> Any:
        return xpath_input


class ToListFloat(EOAbstractListValuesFormatter):
    """
    Format to list of float values
    """

    name = "to_list_float"

    def _format(self, xpath_input: List[str]) -> Any:
        return [float(element) for element in xpath_input]


class ToListInt(EOAbstractListValuesFormatter):
    """
    Format to list of int values
    """

    name = "to_list_int"

    def _format(self, xpath_input: List[str]) -> Any:
        return [int(element) for element in xpath_input]


class ToProcessingHistory(EOAbstractXMLFormatter):
    """Extract processing history from legacy S01 and S03 products (generic functionality)"""

    _product_level = True
    _processing_history: Dict[str, List[Dict[str, str]]] = dict()
    name = "TBD"
    _safe_namespace = "TBD"
    _auxiliary_data_marker = "TBD"

    def _get_attr(self, node: lxml.etree._Element, path: str) -> Any:
        try:
            children = node.xpath(path, namespaces=self._namespaces)
            if isinstance(children, list) and len(children) > 0:
                return str(children[0])
            else:
                return None
        except Exception as err:
            self._logger.error(f"Can not extract xml element from path: {path} due to: {err}")

    def _get_product_output_level(self, node: lxml.etree._Element) -> str:
        product_output_level = PROCESSING_HISTORY_UNKNOWN_MARKER
        # go one level up in the xml hierarchy untill we reach the root node
        while node.getparent() is not None:
            node = node.getparent()  # type: ignore
        if "version" in node.keys():
            version = str(node.attrib["version"])
            level_pattern = r".*[Ll]evel-(\d).*"
            m = match(level_pattern, version)
            if m is not None:
                product_output_level = f"Level-{str(m[1])} Product"

        return product_output_level

    def _parse_xml_history(
        self,
        node: lxml.etree._Element,
        output_level: str = PROCESSING_HISTORY_UNKNOWN_MARKER,
    ) -> None:
        # only nodes which have processing are of interest
        # we filter by outputLevel not to add the processing for each adf
        if node.tag.endswith("processing"):
            # extract data only from processing nodes

            cur_node_data, level = self._retrieve_node_data(node, output_level=output_level)
            if level in self._processing_history.keys():
                self._processing_history[level].append(cur_node_data)
            else:
                self._processing_history[level] = [cur_node_data]

        for child_node in node.getchildren():  # type: ignore
            # parse children
            if "name" in child_node.keys() and self._auxiliary_data_marker not in child_node.attrib["name"]:
                # the adf processing history is not of interest
                self._parse_xml_history(child_node, output_level)

    def _format(self, packed_data: Tuple[lxml.etree._Element, Dict[str, str]]) -> Any:  # type: ignore
        """

        Parameters
        ----------
        input: Any
            input

        Returns
        ----------
        Any:
            Returns the input
        """
        xml_node, self._namespaces = packed_data
        self._processing_history: Dict[str, Any] = dict()

        self._parse_xml_history(xml_node)
        # sort the entries for each level according to the time of processing (ascending)
        return self._processing_history

    def _retrieve_facility(self, node: lxml.etree._Element, node_data: Dict[str, Any]) -> None:

        facility = self._get_attr(node, f"{self._safe_namespace}:facility/@name")
        organisation = self._get_attr(node, f"{self._safe_namespace}:facility/@organisation")
        if facility is not None and organisation is not None:
            node_data[PROCESSING_HISTORY_FACILITY_FIELD] = f"{organisation}-{facility}"
        elif facility is not None:
            node_data[PROCESSING_HISTORY_FACILITY_FIELD] = f"{facility}"
        elif organisation is not None:
            node_data[PROCESSING_HISTORY_FACILITY_FIELD] = f"{organisation}"

    def _retrieve_adfs_and_inputs(self, node: lxml.etree._Element, node_data: Dict[str, Any]) -> None:

        for child_node in node.getchildren():  # type: ignore
            if "role" in child_node.keys():
                if self._auxiliary_data_marker in child_node.attrib["name"]:
                    # all adf should have an AX marker in the name
                    if PROCESSING_HISTORY_ADFS_FIELD not in node_data.keys():
                        # adfs field is not mandatory
                        node_data[PROCESSING_HISTORY_ADFS_FIELD] = list()
                    node_data[PROCESSING_HISTORY_ADFS_FIELD].append(child_node.attrib["name"])
                else:
                    node_data[PROCESSING_HISTORY_INPUTS_FIELD].append(child_node.attrib["name"])

    def _retrieve_node_data(self, node: lxml.etree._Element, output_level: str) -> Tuple[Dict[str, Any], str]:

        node_data: Dict[str, Any] = history_utils.init_history_entry()
        try:
            # processor
            processor = self._get_attr(
                node,
                f"{self._safe_namespace}:facility/{self._safe_namespace}:software/@name",
            )
            if processor is not None:
                node_data[PROCESSING_HISTORY_PROCESSOR_FIELD] = processor

            # version
            version = self._get_attr(
                node,
                f"{self._safe_namespace}:facility/{self._safe_namespace}:software/@version",
            )
            if version is not None:
                node_data[PROCESSING_HISTORY_VERSION_FIELD] = version

            # facility
            self._retrieve_facility(node, node_data)

            # time
            if "stop" in node.keys():
                time = str(node.attrib["stop"])
                if time == PROCESSING_HISTORY_UNKNOWN_MARKER:
                    node_data[PROCESSING_HISTORY_TIME_FIELD] = PROCESSING_HISTORY_UNKNOWN_TIME_MARKER

                else:
                    # make sure the time has the UTC marker
                    if not time.endswith("Z"):
                        time += "Z"
                    node_data[PROCESSING_HISTORY_TIME_FIELD] = time

            # extract adfs and inputs
            self._retrieve_adfs_and_inputs(node, node_data)

            # extract outputs
            parent_node = node.getparent()
            if parent_node is not None and "name" in parent_node.keys():
                node_data[PROCESSING_HISTORY_OUTPUTS_FIELD] = [parent_node.attrib["name"]]

            output_level = self._determine_output_level(node, node_data)

        except Exception as err:
            self._logger.error(f"Can not extract processing history node data due to: {err}")

        return node_data, output_level

    def _determine_output_level(self, node: lxml.etree._Element, node_data: Dict[str, Any]) -> str:
        raise NotImplementedError()


class ToProcessingHistoryS01(ToProcessingHistory):
    """Extract processing history from legacy S01 products"""

    name = "to_processing_history_s01"
    _safe_namespace = "safe"
    _auxiliary_data_marker = "AUX"

    def _determine_output_level_based_on_outputs(self, node_data: Dict[str, Any]) -> Optional[str]:

        s1_product_name_pattern = r".*S1[A-D]_[A-Z0-9]{2}_[A-Z0-9_]{4}_(\d).*"
        level_pattern = r".*[Ll]evel.?(\d).*"
        if len(node_data[PROCESSING_HISTORY_OUTPUTS_FIELD]) > 0:
            m = match(s1_product_name_pattern, node_data[PROCESSING_HISTORY_OUTPUTS_FIELD][0])
            if m is not None:
                return f"Level-{str(m[1])} Product"
            m = match(level_pattern, node_data[PROCESSING_HISTORY_OUTPUTS_FIELD][0])
            if m is not None:
                return f"Level-{str(m[1])} Product"

        return None

    def _determine_output_level_based_on_inputs(self, node_data: Dict[str, Any]) -> Optional[str]:

        s1_product_name_pattern = r".*S1[A-D]_[A-Z0-9]{2}_[A-Z0-9_]{4}_(\d).*"
        level_pattern = r".*[Ll]evel.?(\d).*"
        if len(node_data[PROCESSING_HISTORY_INPUTS_FIELD]) > 0:
            m = match(s1_product_name_pattern, node_data[PROCESSING_HISTORY_INPUTS_FIELD][0])
            if m is not None:
                return f"Level-{str(m[1])} Product"
            m = match(level_pattern, node_data[PROCESSING_HISTORY_INPUTS_FIELD][0])
            if m is not None:
                return f"Level-{str(m[1])} Product"

        return None

    def _determine_output_level(self, node: lxml.etree._Element, node_data: Dict[str, Any]) -> str:

        # the product level is the first entry in the xml history
        # this entry does not have outputs or much information from where we can deduce the output level
        # hence we retrieve this level from the root node of the manifest
        if self._product_level is True:
            self._product_level = False
            return self._get_product_output_level(node)

        parent_node = node.getparent()
        if parent_node is not None and "role" in parent_node.keys():
            role = str(parent_node.attrib["role"])
            m = match(PROCESSING_HISTORY_OUTPUT_LEVEL_PATTERN, role)
            if m is not None:
                return role
            elif role == "Raw Data":
                return "Level-0 Product"
            else:
                pass

        output_based_level = self._determine_output_level_based_on_outputs(node_data)
        if output_based_level is not None:
            return output_based_level

        input_based_level = self._determine_output_level_based_on_inputs(node_data)
        if input_based_level is not None:
            return input_based_level

        return PROCESSING_HISTORY_UNKNOWN_MARKER


class ToProcessingHistoryS03(ToProcessingHistory):
    """Extract processing history from legacy S03 products"""

    name = "to_processing_history_s03"
    _safe_namespace = "sentinel-safe"
    _auxiliary_data_marker = "AX"

    def _determine_output_level(self, node: lxml.etree._Element, node_data: Dict[str, Any]) -> str:

        # the product level is the first entry in the xml history
        # this entry does not have outputs or much information from where we can deduce the output level
        # hence we retrieve this level from the root node of the manifest
        if self._product_level is True:
            self._product_level = False
            return self._get_product_output_level(node)

        if "outputLevel" in node.keys():
            return f"Level-{str(node.attrib['outputLevel'])} Product"

        s3_product_name_pattern = r".*S3[A-D]_[A-Z]{2}_(\d).*"
        if len(node_data[PROCESSING_HISTORY_OUTPUTS_FIELD]) > 0:
            m = match(s3_product_name_pattern, node_data[PROCESSING_HISTORY_OUTPUTS_FIELD][0])
            if m is not None:
                return f"Level-{str(m[1])} Product"

        return PROCESSING_HISTORY_UNKNOWN_MARKER


class ToBoolInt(EOAbstractSingleValueFormatter):
    """Formatter for converting a string to an integer representation of bool"""

    # docstr-coverage: inherited
    name = "to_bool_int"

    def _format(self, xpath_input: str) -> int:
        return int("true" == xpath_input.lower())


class ToProcessingSoftware(EOAbstractXMLFormatter):
    """Formatter for extracting processing software from xml"""

    # docstr-coverage: inherited
    name = "to_processing_software"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> dict[str, str]:
        """retrieve the name and version of the xml node xpath_input"""
        try:
            dict_attrib = xpath_input[0].attrib
            return {str(dict_attrib["name"]): str(dict_attrib["version"])}
        except Exception as e:
            self._logger.debug(f"{self.name}: {e}")
            return {"": ""}


class ToSciDOI(EOAbstractListValuesFormatter):
    """Formatter for extracting product doi from xml"""

    # docstr-coverage: inherited
    name = "to_sci_doi"

    def _format(self, xpath_input: List[str]) -> str:
        # retrieve the right part of the DOI url
        try:
            if xpath_input and len(xpath_input) == 1:
                return xpath_input[0].replace("https://doi.org/", "")
        except Exception:
            self._logger.warning("Can not retrieve sci:doi", exc_info=True)
        return ""


class ToProductTimeliness(EOAbstractSingleValueFormatter):
    """Formatter for getting the timeliness for specific timeliness"""

    # docstr-coverage: inherited
    name = "to_product_timeliness"

    def _format(self, xpath_input: str) -> str:
        timeliness_category = xpath_input
        to_timeliness_map = {
            "NR": "PT3H",
            "NRT": "PT3H",
            "NRT-3h": "PT3H",
            "ST": "PT36H",
            "24H": "PT24H",
            "STC": "PT36H",
            "Fast-24h": "PT24H",
            "AL": "Null",
            "NT": "P1M",
            "NTC": "P1M",
        }
        if timeliness_category in to_timeliness_map:
            return to_timeliness_map[timeliness_category]
        return "Null"


class ToUTMZone(EOAbstractSingleValueFormatter):
    """Formatter for getting the utm zone"""

    # docstr-coverage: inherited
    name = "to_utm_zone"

    def _format(self, xpath_input: str) -> str:
        # read https://github.com/stac-extensions/product/blob/main/README.md
        # to be modified based on what is present in xml_accessors.py workaround of this accessor: TODO
        utm_zone = xpath_input.split("/")
        if len(utm_zone) < 2:
            raise FormattingError("No L1C UTM zone format found")
        return utm_zone[1].lstrip()


class ToSatOrbitState(EOAbstractListValuesFormatter):
    """Formatter for getting the correct orbit state"""

    # docstr-coverage: inherited
    name = "to_sat_orbit_state"

    def _format(self, xpath_input: List[str]) -> str:
        """There are cases when that xml data is with uppercase or
        it has several xml data attributes about ascending, descending, etc"""
        # the data might come in uppercase | has usage for S1 products
        if xpath_input and len(xpath_input) == 1:
            return xpath_input[0].lower()
        return "No data about orbit state"


class ToProviders(EOAbstractSingleValueFormatter):
    """Formatter for respecting providers stac standard"""

    # docstr-coverage: inherited
    name = "to_providers"

    def _format(self, xpath_input: str) -> Any:
        """Function that returns the input without formatting"""
        return xpath_input


class ToPlatform(EOAbstractSingleValueFormatter):
    """Formatter for the platform attribute compliant with the stac standard"""

    # docstr-coverage: inherited
    name = "to_platform"

    def _format(self, xpath_input: str) -> Any:
        """The platform's name retrived from the resulted list from XML search"""
        if isinstance(xpath_input, str) and xpath_input is not None:
            return str(xpath_input).lower()
        raise FormattingError("No data about stac_discovery/properties/platform")


class ToSarPolarizations(EOAbstractListValuesFormatter):
    """Formatter for sar:polarizations attribute"""

    # docstr-coverage: inherited
    name = "to_sar_polarizations"

    def _format(self, xpath_input: List[str]) -> Any:
        """The input parameter from this function should be a list with all polarizations"""
        if isinstance(xpath_input, list):
            return xpath_input
        raise FormattingError("The xml path for sar:polarizations is wrong or it doesn't exist!")


class TomissingElements(EOAbstractXMLFormatter):
    """Formatter for data_information:missing_elements attribute"""

    # docstr-coverage: inherited
    name = "to_missing_elements"

    def _format(self, xpath_input: List[lxml.etree._Element]) -> list[dict[str, str]]:
        if not isinstance(xpath_input, list):
            raise FormattingError(
                "The xml path for other_metadata/data_information/missing_elements is wrong or it doesn't exist!",
            )
        ret_value = []
        for child in xpath_input:
            start_time = child.get("startTime")
            stop_time = child.get("stopTime")
            if start_time and stop_time:
                item = {"start_time": start_time, "stop_time": stop_time}
                ret_value.append(item)
        return ret_value


class ToDegradationFlags(EOAbstractSingleValueFormatter):
    """Formatter for the degradation_flags attribute"""

    # docstr-coverage: inherited
    name = "to_degradation_flags"

    def _format(self, xpath_input: str) -> Any:
        if isinstance(xpath_input, str) and xpath_input is not None:
            return str(xpath_input).lower().split()
        raise FormattingError("No data about other_metadata/data_information/degradation_flags")


class ToS02Adfs(EOAbstractGenericXMLFormatter):
    """Formatter for S02 processing history adfs extraction"""

    # docstr-coverage: inherited
    name = "to_s02_adfs"

    def _format(self, xpath_input: Tuple[lxml.etree._Element, str]) -> Any:
        """The input parameter from this function should be a list with all polarizations"""
        from ast import literal_eval

        adf_list = list()
        # should get the AUXILIARY_DATA_INFO xml node from MTD_MSIL1C/L2A
        aux_data_info_node: lxml.etree._Element = xpath_input[0]
        # sub elements of AUXILIARY_DATA_INFO serialised as str of list
        sub_paths_as_str: str = xpath_input[1]
        sub_paths: List[str] = literal_eval(sub_paths_as_str)
        for sub_path in sub_paths:
            sub_elements = aux_data_info_node.xpath(sub_path)
            if isinstance(sub_elements, list):
                for sub_elem in sub_elements:
                    if isinstance(sub_elem, lxml.etree._Element):
                        sub_elem_text = sub_elem.text
                        if sub_elem_text != "None":
                            adf_list.append(sub_elem.text)

        return adf_list
