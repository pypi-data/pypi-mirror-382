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

l0_writers.py


Dedicated module to manually write L0 products


"""
import re
from pathlib import Path
from typing import cast

import numpy as np
from jinja2 import Environment, FileSystemLoader

from eopf import EOProduct
from eopf.accessor.memmap_accessors_impl import FixedMemMap, MemMap
from eopf.common.file_utils import AnyPath
from eopf.exceptions.errors import EOProductError
from eopf.product.eo_variable import EOVariable


class L0Writers:
    """
    L0Writers class

    """

    @staticmethod
    def S3L0Writer(source: EOProduct, url: str | AnyPath) -> None:
        """
        Statix S3 L0 writers

        Parameters
        ----------
        source
        url

        Returns
        -------

        """
        filename = AnyPath.cast(url)
        filename.mkdir(exist_ok=True)

        ispdat = MemMap(
            filename / "ISPData.dat",
            primary_header_length_bytes=6,
            ancillary_header_length_bytes=0,
            packet_length_start_position_bytes=4,
            packet_length_stop_position_bytes=6,
        )
        # verify mandatory variables
        packet_data_length = source["/conditions/packet_data_length"]
        if not isinstance(packet_data_length, EOVariable):
            raise EOProductError("missing variable for l0 writer : packet_data_length")
        isp = source["/measurements/isp"]
        if not isinstance(isp, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        if "gps_time_days" not in isp.coords:
            raise EOProductError("missing coordinate for l0 writer")
        if "gps_time_seconds" not in isp.coords:
            raise EOProductError("missing coordinate for l0 writer")
        if "gps_time_microseconds" not in isp.coords:
            raise EOProductError("missing coordinate for l0 writer")

        ispdat.build_buffer(np.asarray(packet_data_length.data))

        ispdat.write_key(0, 3, np.asarray([source.attrs["other_metadata"]["packet_version"]]), "s_uint8")
        ispdat.write_key(3, 1, np.asarray([source.attrs["other_metadata"]["packet_type"]]), "s_uint8")
        ispdat.write_key(4, 1, np.asarray([source.attrs["other_metadata"]["header_flag"]]), "s_bool")
        ispdat.write_key(16, 2, np.asarray([source.attrs["other_metadata"]["sequence_flag"]]), "s_uint8")

        ispdat.write_key(32, 16, np.asarray(packet_data_length.data), "uint8")
        ispdat.write_key(49, 7, np.asarray([source.attrs["other_metadata"]["packet_category"]]), "s_uint8")

        ispdat.write_key(144, -1, np.asarray(isp.data), "var_bytearray")

        ispdat.save_buffer()
        ispdat.reset()

        ispann = FixedMemMap(url + "/ISPAnnotation.dat", fixed_packet_length_bytes=30)
        ispann.build_buffer(np.asarray(packet_data_length.data).size)

        ispann.write_key(0, 32, np.asarray(isp.coords["gps_time_days"].data), "uint32")
        ispann.write_key(
            32,
            32,
            np.asarray(isp.coords["gps_time_seconds"].data),
            "uint32",
        )
        ispann.write_key(
            64,
            32,
            np.asarray(isp.coords["gps_time_microseconds"].data),
            "uint32",
        )

        ispann.save_buffer()
        ispann.reset()

        cur_file_path = Path(__file__).absolute()
        templates_folder_path = cur_file_path.parent.joinpath("templates")
        env = Environment(loader=FileSystemLoader(templates_folder_path), autoescape=True)
        templateS3L0 = env.get_template("S03_L0_manifest.xml")
        attrs = {"PRODUCT": source.attrs}
        output = templateS3L0.render(attrs)

        with (filename / "xfdumanifest.xml").open("w") as f:
            f.write(output)

    @staticmethod
    def S1L0Writer(source: EOProduct, url: str | AnyPath) -> None:
        """
        Staticx S1 L0 product writer

        Parameters
        ----------
        source
        url

        Returns
        -------

        """

        out_dir = AnyPath.cast(url)
        out_dir.mkdir(exist_ok=True)

        # file name reconstruction based on the name of the output file
        match = re.search(
            r"(S1[ABCD])_(..)_RAW__0S.._(\d{8}T\d{6})_(\d{8}T\d{6})_(\d{6})_(\w{6})",
            out_dir.path,
        )
        if match:
            file_name_pattern = (
                match[1].lower()
                + "-"  # mission
                + match[2].lower()
                + "-"  # mode
                + "raw"
                + "-"
                + "s-{polarisation}"
                + "-"
                + match[3]
                + "-"  # start time
                + match[4]
                + "-"  # stop time
                + match[5]
                + "-"  # abs orbit number
                + match[6].lower()  # data take
            )
        else:
            file_name_pattern = "ISP-{polarisation}"

        for pola in ["hh", "hv", "vv", "vh"]:
            L0Writers.s1_handle_pola_writings(file_name_pattern, out_dir, pola, source)

        cur_file_path = Path(__file__).absolute()
        templates_folder_path = cur_file_path.parent.parent / "store" / "templates"
        env = Environment(loader=FileSystemLoader(templates_folder_path), autoescape=True)
        attrs = {"PRODUCT": source.attrs, "conditions": source["conditions"].attrs}
        if attrs["PRODUCT"]["stac_discovery"]["properties"]["eopf:instrument_mode"] == "SM":
            templateS1L0 = env.get_template("S01SSMRAW_manifest.xml")
        else:
            templateS1L0 = env.get_template("S01_L0_manifest.xml")
        output = templateS1L0.render(attrs)

        with (out_dir / "manifest.safe").open("w") as f:
            f.write(output)

    @staticmethod
    def s1_handle_pola_writings(file_name_pattern: str, out_dir: AnyPath, polarisation: str, source: EOProduct) -> None:
        """
        Handle S1 polarisation dependent file (hh hv vv etc)
        Parameters
        ----------
        file_name_pattern
        out_dir
        polarisation
        source

        Returns
        -------

        """
        if L0Writers.exists(source, f"/conditions/{polarisation}/packet_sequence_count_{polarisation}"):
            file_name = file_name_pattern.replace("{polarisation}", polarisation) + ".dat"

            L0Writers.s1_l0_handle_isp_data(file_name, out_dir, polarisation, source)

            L0Writers.s1_l0_handle_isp_annot(file_name_pattern, out_dir, polarisation, source)

            L0Writers.s1_l0_handle_isp_index(file_name_pattern, out_dir, polarisation, source)

    @staticmethod
    def s1_l0_handle_isp_data(
        file_name: str,
        out_dir: AnyPath,
        polarisation: str,
        source: EOProduct,
    ) -> None:
        """
        Handle ISP dat files writing
        Parameters
        ----------
        file_name
        out_dir
        polarisation
        source

        Returns
        -------

        """

        list_to_extract: dict[str, EOVariable] = {
            "packet_data_length": cast(
                EOVariable,
                source[f"/conditions/{polarisation}/packet_data_length_{polarisation}"],
            ),
            "packet_sequence_count": cast(
                EOVariable,
                source[f"/conditions/{polarisation}/packet_sequence_count_{polarisation}"],
            ),
            "coarse_time": cast(EOVariable, source[f"/coordinates/coarse_time_{polarisation}"]),
            "fine_time": cast(EOVariable, source[f"/coordinates/fine_time_{polarisation}"]),
            "dataword_index": cast(EOVariable, source[f"/coordinates/dataword_index_{polarisation}"]),
            "space_packet_count": cast(
                EOVariable,
                source[f"/conditions/{polarisation}/space_packet_count_{polarisation}"],
            ),
            "pri_count": cast(EOVariable, source[f"/conditions/{polarisation}/pri_count_{polarisation}"]),
            "error_flag": cast(EOVariable, source[f"/quality/error_flag_{polarisation}"]),
            "baq_mode": cast(EOVariable, source[f"/conditions/{polarisation}/baq_mode"]),
            "baq_length": cast(EOVariable, source[f"/conditions/{polarisation}/baq_length"]),
            "range_decimation": cast(EOVariable, source[f"/conditions/{polarisation}/range_decimation"]),
            "rx_gain": cast(EOVariable, source[f"/conditions/{polarisation}/rx_gain"]),
            "tx_ramp_rate": cast(EOVariable, source[f"/conditions/{polarisation}/tx_ramp_rate"]),
            "tx_pulse_start_freq": cast(EOVariable, source[f"/conditions/{polarisation}/tx_pulse_start_freq"]),
            "tx_pulse_length": cast(EOVariable, source[f"/conditions/{polarisation}/tx_pulse_length"]),
            "rank": cast(EOVariable, source[f"/conditions/{polarisation}/rank"]),
            "pri": cast(EOVariable, source[f"/conditions/{polarisation}/pri"]),
            "swst": cast(EOVariable, source[f"/conditions/{polarisation}/swst"]),
            "swl": cast(EOVariable, source[f"/conditions/{polarisation}/swl"]),
            "ssb_message": cast(EOVariable, source[f"/conditions/{polarisation}/ssb_message"]),
            "number_of_quads": cast(EOVariable, source[f"/conditions/{polarisation}/number_of_quads"]),
            "user_data": cast(EOVariable, source[f"/measurements/user_data_{polarisation}"]),
        }
        for s, f in list_to_extract.items():
            if not isinstance(f, EOVariable):
                raise EOProductError(f"missing variable {s} for l0 writer")

        ispdat = MemMap(
            out_dir / file_name,
            primary_header_length_bytes=6,
            ancillary_header_length_bytes=0,
            packet_length_start_position_bytes=4,
            packet_length_stop_position_bytes=6,
        )
        ispdat.build_buffer(np.asarray(list_to_extract["packet_data_length"].data))
        ispdat.write_key(0, 3, np.asarray(source.attrs["other_metadata"]["packet_version"]), "s_uint8")
        ispdat.write_key(3, 1, np.asarray(source.attrs["other_metadata"]["packet_type"]), "s_bool")
        ispdat.write_key(
            4,
            1,
            np.asarray(source.attrs["other_metadata"]["header_flag"]),
            "s_bool",
        )
        ispdat.write_key(
            5,
            7,
            np.asarray(source.attrs["other_metadata"]["application_process_identifer"]),
            "s_uint8",
        )
        ispdat.write_key(12, 4, np.asarray(source.attrs["other_metadata"]["packet_category"]), "s_uint8")
        ispdat.write_key(16, 2, np.asarray(source.attrs["other_metadata"]["sequence_flag"]), "s_uint8")
        ispdat.write_key(
            18,
            14,
            np.asarray(list_to_extract["packet_sequence_count"].data),
            "uint16",
        )
        ispdat.write_key(
            32,
            16,
            np.asarray(list_to_extract["packet_data_length"].data),
            "uint8",
        )
        ispdat.write_key(48, 32, np.asarray(list_to_extract["coarse_time"].data), "uint32")
        ispdat.write_key(80, 16, np.asarray(list_to_extract["fine_time"].data), "uint16")
        ispdat.write_key(
            96,
            32,
            np.asarray(source.attrs["other_metadata"]["synchronisation_marker"]),
            "s_uint32",
        )
        ispdat.write_key(
            128,
            32,
            np.asarray(source.attrs["stac_discovery"]["properties"]["eopf:data_take_id"]),
            "s_uint32",
        )
        ispdat.write_key(160, 8, np.asarray(source.attrs["other_metadata"]["event_control_code"]), "s_uint8")
        ispdat.write_key(169, 3, np.asarray(source.attrs["other_metadata"]["test_mode"]), "s_uint8")
        ispdat.write_key(
            172,
            4,
            np.asarray(source.attrs["other_metadata"][f"{polarisation}_receive_channel_id"]),
            "s_uint8",
        )
        ispdat.write_key(
            176,
            32,
            np.asarray(source.attrs["other_metadata"]["instrument_configuration_id"]),
            "s_uint32",
        )
        ispdat.write_key(
            208,
            8,
            np.asarray(list_to_extract["dataword_index"].data),
            "uint8",
        )
        ispdat.write_key(
            232,
            32,
            np.asarray(list_to_extract["space_packet_count"].data),
            "uint32",
        )
        ispdat.write_key(264, 32, np.asarray(list_to_extract["pri_count"].data), "uint32")
        ispdat.write_key(296, 1, np.asarray(list_to_extract["error_flag"].data), "bool")
        ispdat.write_key(299, 5, np.asarray(list_to_extract["baq_mode"].data), "uint8")
        ispdat.write_key(304, 8, np.asarray(list_to_extract["baq_length"].data), "uint8")
        ispdat.write_key(
            320,
            8,
            np.asarray(list_to_extract["range_decimation"].data),
            "uint8",
        )
        ispdat.write_key(328, 8, np.asarray(list_to_extract["rx_gain"].data), "uint8")
        ispdat.write_key(
            336,
            16,
            np.asarray(list_to_extract["tx_ramp_rate"].data),
            "uint16",
        )
        ispdat.write_key(
            352,
            16,
            np.asarray(list_to_extract["tx_pulse_start_freq"].data),
            "uint16",
        )
        ispdat.write_key(
            368,
            24,
            np.asarray(list_to_extract["tx_pulse_length"].data),
            "uint32",
        )
        ispdat.write_key(395, 5, np.asarray(list_to_extract["rank"].data), "uint8")
        ispdat.write_key(400, 24, np.asarray(list_to_extract["pri"].data), "uint32")
        ispdat.write_key(424, 24, np.asarray(list_to_extract["swst"].data), "uint32")
        ispdat.write_key(448, 24, np.asarray(list_to_extract["swl"].data), "uint32")
        ispdat.write_key(
            472,
            48,
            np.asarray(list_to_extract["ssb_message"].data),
            "bytearray",
        )
        ispdat.write_key(
            520,
            16,
            np.asarray(list_to_extract["number_of_quads"].data),
            "uint16",
        )
        ispdat.write_key(
            544,
            -1,
            np.asarray(list_to_extract["user_data"].data),
            "var_bytearray",
        )
        ispdat.save_buffer()
        ispdat.reset()

    @staticmethod
    def s1_l0_handle_isp_annot(
        file_name_pattern: str,
        out_dir: AnyPath,
        polarisation: str,
        source: EOProduct,
    ) -> None:
        """
        Handle ISP annotation file writing

        Parameters
        ----------
        file_name_pattern
        out_dir
        polarisation
        source

        Returns
        -------

        """
        variable_paths: dict[str, str] = {
            "packet_data_length": f"/conditions/{polarisation}/packet_data_length_{polarisation}",
            "sensing_time_days": f"/coordinates/sensing_time_days_{polarisation}",
            "sensing_time_millisec": f"/coordinates/sensing_time_millisec_{polarisation}",
            "sensing_time_microsec": f"/coordinates/sensing_time_microsec_{polarisation}",
            "downlink_time_days": f"/coordinates/downlink_time_days_{polarisation}",
            "downlink_time_millisec": f"/coordinates/downlink_time_millisec_{polarisation}",
            "downlink_time_microsec": f"/coordinates/downlink_time_microsec_{polarisation}",
            "frames": f"/conditions/{polarisation}/frames",
            "missing_frames": f"/conditions/{polarisation}/missing_frames",
            "crc_flag": f"/quality/crc_flag_{polarisation}",
            "vcid_present_flag": f"/conditions/{polarisation}/vcid_present_flag",
            "vcid": f"/conditions/{polarisation}/vcid",
            "channel": f"/conditions/{polarisation}/channel",
        }

        variables: dict[str, EOVariable] = {}

        for name, path in variable_paths.items():
            var = source[path]
            if not isinstance(var, EOVariable):
                raise EOProductError(f"missing variable for l0 writer: {name}")
            variables[name] = var

        file_name = file_name_pattern.replace("{polarisation}", polarisation) + "-annot.dat"
        ispann = FixedMemMap(out_dir / file_name, fixed_packet_length_bytes=26)
        ispann.build_buffer(np.asarray(variables["packet_data_length"].data).size)
        ispann.write_key(
            0,
            16,
            np.asarray(variables["sensing_time_days"].data),
            "uint16",
        )
        ispann.write_key(
            16,
            32,
            np.asarray(variables["sensing_time_millisec"].data),
            "uint32",
        )
        ispann.write_key(
            48,
            16,
            np.asarray(variables["sensing_time_microsec"].data),
            "uint16",
        )
        ispann.write_key(
            64,
            16,
            np.asarray(variables["downlink_time_days"].data),
            "uint16",
        )
        ispann.write_key(
            80,
            32,
            np.asarray(variables["downlink_time_millisec"].data),
            "uint32",
        )
        ispann.write_key(
            112,
            16,
            np.asarray(variables["downlink_time_microsec"].data),
            "uint16",
        )
        ispann.write_key(
            128,
            16,
            np.asarray(variables["packet_data_length"].data),
            "uint16",
        )
        ispann.write_key(144, 16, np.asarray(variables["frames"].data), "uint16")
        ispann.write_key(
            160,
            16,
            np.asarray(variables["missing_frames"].data),
            "uint16",
        )
        ispann.write_key(176, 8, np.asarray(variables["crc_flag"].data), "bool")
        ispann.write_key(
            184,
            1,
            np.asarray(variables["vcid_present_flag"].data),
            "bool",
        )
        ispann.write_key(186, 6, np.asarray(variables["vcid"].data), "uint8")
        ispann.write_key(192, 2, np.asarray(variables["channel"].data), "s_uint8")
        ispann.save_buffer()
        ispann.reset()

    @staticmethod
    def s1_l0_handle_isp_index(file_name_pattern: str, out_dir: AnyPath, polarisation: str, source: EOProduct) -> None:
        """
        Handles S1 ISP index idx files
        Parameters
        ----------
        file_name_pattern
        out_dir
        polarisation
        source

        Returns
        -------

        """
        date_time = source[f"/conditions/index/{polarisation}/date_time"]
        if not isinstance(date_time, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        date_time = source[f"/conditions/index/{polarisation}/date_time"]
        if not isinstance(date_time, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        delta_time = source[f"/conditions/index/{polarisation}/delta_time"]
        if not isinstance(delta_time, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        delta_size = source[f"/conditions/index/{polarisation}/delta_size"]
        if not isinstance(delta_size, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        data_offset = source[f"/conditions/index/{polarisation}/data_offset"]
        if not isinstance(data_offset, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        byte_offset = source[f"/conditions/index/{polarisation}/byte_offset"]
        if not isinstance(byte_offset, EOVariable):
            raise EOProductError("missing variable for l0 writer")
        var_size_flag = source[f"/conditions/index/{polarisation}/var_size_flag"]
        if not isinstance(var_size_flag, EOVariable):
            raise EOProductError("missing variable for l0 writer")

        file_name = file_name_pattern.replace("{polarisation}", polarisation) + "-index.dat"
        ispidx = FixedMemMap(out_dir / file_name, fixed_packet_length_bytes=36)
        ispidx.build_buffer(np.asarray(date_time.data).size)
        ispidx.write_key(
            0,
            64,
            np.asarray(date_time.data),
            "uint64",
        )
        ispidx.write_key(
            64,
            64,
            np.asarray(delta_time.data),
            "uint64",
        )
        ispidx.write_key(
            128,
            32,
            np.asarray(delta_size.data),
            "uint32",
        )
        ispidx.write_key(
            160,
            32,
            np.asarray(data_offset.data),
            "uint32",
        )
        ispidx.write_key(
            192,
            64,
            np.asarray(byte_offset.data),
            "uint64",
        )
        ispidx.write_key(
            256,
            8,
            np.asarray(var_size_flag.data),
            "bool",
        )
        ispidx.save_buffer()
        ispidx.reset()

    # TODO move to EOProduct directly !!!
    @staticmethod
    def exists(product: EOProduct, the_path: str) -> bool:
        """
        test if exist in product
        Parameters
        ----------
        product
        the_path

        Returns
        -------

        """
        try:
            product[the_path]
            return True
        except KeyError:
            return False
