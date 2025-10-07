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
eo_qc_processor.py

EOQC Processor implementation

"""

import json
import time
from dataclasses import asdict
from typing import Any, List, Mapping, Optional, Union

from eopf import EOContainer, EOGroup, EOLogging
from eopf.common import date_utils
from eopf.common.file_utils import AnyPath
from eopf.exceptions import InvalidProductError
from eopf.product.eo_product import EOProduct
from eopf.qualitycontrol.eo_qc import EOQCCheckResult
from eopf.qualitycontrol.eo_qc_config import EOQCConfig, EOQCConfigBuilder


class EOQCProcessor:
    """
    Class that orchestrate the checks on products

    Parameters
    ----------
    config_folder : Optional[Union[AnyPath,str]]
        Optional config folder containing the json checklist.
        Inspection files have name "*_inspections.json".
        Default to EOConfiguration().qualitycontrol__folder that default point to eopf/qualitycontrol/config.
        If set to None no configuration will be loaded and it has to be handled through processor.qc_config_builder

    parameters : Optional[dict[str,Any]]
        Parameters dict to replace in inspection. for example @@@V_MIN@@@ will be
        replaced by the V_MIN entry of this dict. If some @@@KEY@@@ are not replaced an exception will occur.
        Default None

    update_attrs : bool,optional
        Turn on or off updating the eoproduct quality attributes to add the "qc" report. Default to True

    report_path : Optional[Union[AnyPath,str]]
        Folder to write the report to, filename will be : QC_report_{eoproduct_name}.json. Default None

    config_path : Optional[Union[AnyPath,str]]
        Use this json checklist instead of the default found one by EOQCConfigBuilder. Default None

    additional_config_folders : Optional[list[Union[AnyPath,str]]]
        Add these folders to the EOQCConfigBuilder to search for checklists and inspections

    Attributes
    ----------
    qc_config_builder  : EOQCConfigBuilder
        internal EOQCConfigBuilder


    """

    def __init__(
        self,
        config_folders: Optional[List[Union[AnyPath, str]]] = None,
        parameters: Optional[dict[str, Any]] = None,
        update_attrs: bool = True,
        report_path: Optional[Union[AnyPath, str]] = None,
    ) -> None:
        """

        Parameters
        ----------
        config_folders (Optional[List[Union[AnyPath,str]]]) :
            Optional config folders containing the json checklists.
            Inspection files have name "*_inspections.json".
            Default to EOConfiguration().qualitycontrol__folder that default point to eopf/qualitycontrol/config.
            If set to empty list [] no configuration will be loaded and it has to be handled through
            processor.qc_config_builder

        parameters (Optional[dict[str,Any]]) :
            Parameters dict to replace in inspection. for example @@@V_MIN@@@ will be
            replaced by the V_MIN entry of this dict. If some @@@KEY@@@ are not replaced an exception will occur.
            Default None

        update_attrs (bool,optional) :
            Turn on or off updating the eoproduct quality attributes to add the "qc" report. Default to True
        report_path (Optional[Union[AnyPath,str]]) :
            Folder to write the report to, filename will be : QC_report_{eoproduct_name}.json. Default None

        Returns
        -------
            None
        """
        self._logger = EOLogging().get_logger("eopf.quality_control")
        self._qc_config_builder: EOQCConfigBuilder = EOQCConfigBuilder(config_folders)
        self._qc_parameters: Optional[dict[str, Any]] = parameters
        self._update_attrs: bool = update_attrs
        self._write_report: bool = report_path is not None
        if not self._write_report and not self._update_attrs:
            raise ValueError("Neither update_attr nor write_report are activated, doing nothing !!!")
        self._report_path: Optional[AnyPath] = AnyPath.cast(report_path) if report_path is not None else None
        if self._write_report:
            if self._report_path is None:
                raise ValueError("Can't write report no path given")

    @property
    def qc_config_builder(self) -> EOQCConfigBuilder:
        """
        Get the config builder instance
        Returns
        -------
        The builder instance
        """
        return self._qc_config_builder

    def __repr__(self) -> str:
        """

        Returns
        -------
        str repr
        """
        return f"[{id(self)}]{str(self)}"

    def check(self, eo_object: EOProduct | EOContainer, sub_path: str = "") -> EOProduct | EOContainer:
        """Execute all checks of the .

        Parameters
        ----------
        eo_object: EOProduct| EOContainer
            EOProduct | EOContainer to check
        sub_path

        Returns
        -------
        EOProduct| EOContainer
            The controlled products. If update_attrs then the reports will be in the attrs
        """
        self._logger.debug(f"Checking {eo_object.name}")
        self._check_eo_object(eo_object)
        sub_path = sub_path + "_" if len(sub_path) != 0 else ""
        if isinstance(eo_object, EOContainer):
            for v in eo_object.values():
                if isinstance(v, EOProduct):
                    self._check_eo_object(v, sub_path + eo_object.name + "_")
                else:
                    self.check(v, sub_path + eo_object.name + "_")
        return eo_object

    def _check_eo_object(self, eo_object: EOProduct | EOContainer, sub_path: str = "") -> EOProduct | EOContainer:
        """
        Internal check on eo object
        Parameters
        ----------
        eo_object : the object to check
        sub_path : sub path to have the hierachy in the report

        Returns
        -------
        The analysed eo_object
        """
        data_type = eo_object.product_type if isinstance(eo_object, EOProduct) else eo_object.container_type
        if not data_type:
            if isinstance(eo_object, EOProduct):
                raise InvalidProductError(f"Missing product type in product {sub_path} /{eo_object.name}")
            raise InvalidProductError(f"Missing container type in container {sub_path} / {eo_object.name}")
        qc_config = self._qc_config_builder.get_qc_config(data_type, self._qc_parameters)

        # Dict of qc_id:qc_results
        qc_results_dict = {}
        qc_global_status = True
        # Run check(s) of the configuration
        for qc_id, qc in qc_config.inspection_dict.items():
            start_time = time.time()
            self._logger.debug(f"Running inspection : {qc_id}")
            try:
                qc_result: EOQCCheckResult = qc.check(eo_object)
                qc_results_dict[qc_id] = qc_result
                qc_global_status = qc_global_status and qc_result.status
            except Exception as e:
                self._logger.exception(f"An error occurred in {qc_id} : {e}")
                raise
            elapsed_time = time.time() - start_time
            self._logger.debug(f"Duration for {qc_id}: {elapsed_time:.2f} seconds")
        self._logger.debug(f"{eo_object.name} has EOQC status : {qc_global_status}")
        # Gen report content
        report: Mapping[str, Any] = self._gen_report(eo_object, qc_results_dict, qc_global_status, qc_config)
        # If true it update the quality attribute of the product.
        if self._update_attrs:
            self._update_attributes(eo_object, report)
        # If the it write the quality control report in a .json file.
        if self._write_report:
            if self._report_path is not None:
                self._write_report_to_file(eo_object.name, report, sub_path)
            else:
                raise ValueError("Can't write report no path given")
        return eo_object

    @staticmethod
    def _update_attributes(eo_object: EOProduct | EOContainer, report: Mapping[str, Any]) -> None:
        """
        This method update the EOProduct quality group attributes with the results of quality control.

        Parameters
        ----------
        eoproduct (EOProduct) :
            EOProduct to check
        report (Mapping[str, Any]):
            report to write in product  quality group attributes

        """
        if isinstance(eo_object, EOProduct):
            if "quality" not in eo_object:
                eo_object["quality"] = EOGroup("quality")
            # Alway overwrite existing qc
            eo_object.quality.attrs["qc"] = report

    def _write_report_to_file(self, eoproduct_name: str, report: Mapping[str, Any], sub_path: str = "") -> None:
        """

        This method write the quality control report in json in given location.

        Parameters
        ----------
        report(Mapping[str, Any]): report dict to write to file
        eoproduct_name (str) : EOProduct name


        Returns
        -------
        bool
            Has the quality control report been successfully written, true is ok, false if not.
        """
        if self._report_path is None:
            raise ValueError("Can't write report no path given")

        report_path = self._report_path / f"QC_report_{sub_path}{eoproduct_name}.json"

        try:
            with report_path.open("w") as outfile:
                json.dump(report, outfile, indent=4)
        except IOError as e:
            self._logger.error("An error is occured while trying to write the QC Report : %s", e)
            raise e

    def _gen_report(
        self,
        eo_object: EOProduct | EOContainer,
        qc_results_dict: dict[str, EOQCCheckResult],
        qc_global_status: bool,
        qc_config: EOQCConfig,
    ) -> Mapping[str, Any]:
        """
        Generate the quality report

        Parameters
        ----------
        eo_object : analysed eo_object
        qc_results_dict :  dict of results
        qc_global_status : global status
        qc_config : The config used

        Returns
        -------
        the report dict
        """
        report: dict[str, Any] = {
            "product_name": eo_object.name,
            "product_type": eo_object.product_type if isinstance(eo_object, EOProduct) else eo_object.container_type,
            "qc_config_version": qc_config.version,
            "qc_config_identifier": qc_config.identifier,
            "inspection_date": date_utils.get_utc_str_now(),
            "global_status": "PASSED" if qc_global_status else "FAILED",
            "inspections": {},
        }

        try:
            report.update(
                {
                    "start_datetime": eo_object.attrs["stac_discovery"]["properties"]["start_datetime"],
                    "end_datetime": eo_object.attrs["stac_discovery"]["properties"]["end_datetime"],
                    "relative_orbit": eo_object.attrs["stac_discovery"]["properties"]["sat:relative_orbit"],
                    "absolute_orbit": eo_object.attrs["stac_discovery"]["properties"]["sat:absolute_orbit"],
                },
            )
        except KeyError as e:
            self._logger.error(f"Missing attributes in product : {e}")
            raise InvalidProductError(f"Missing attributes in product {e}") from e

        for qc_id, qc_result in qc_results_dict.items():
            report["inspections"][qc_id] = asdict(qc_result)

        return report
