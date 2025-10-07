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
cli_convert.py


cli implementation for conversion tool


"""
from typing import Any

import click

from eopf import EOConfiguration, __version__, convert
from eopf.cli.cli import EOPFPluginCommandCLI
from eopf.logging import EOLogging
from eopf.store.zarr import ZARR_PRODUCT_FORMAT


class EOCLIConvert(EOPFPluginCommandCLI):
    """EO cli command to Merge L1C/L2A S2 products.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "convert"
    cli_params: list[click.Parameter] = [
        click.Argument(["source_path"], type=click.Path()),
        click.Argument(["target_path"], type=click.Path()),
        click.Option(["--target_format"], type=str, default=ZARR_PRODUCT_FORMAT),
        click.Option(["--mask_and_scale"], type=bool),
        click.Option(["--mapping-folder"], type=click.Path()),
    ]
    help = (
        "Convert a product to an other format\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  source_path = Source product to convert\n\n"
        "  target_path = Product to write the result to or directory\n\n"
        "  [--target_format] = specify the target format if directory given (ex: zarr)\n\n"
        "  [--mask_and_scale] = specify mask and scale option (true/false)\n\n"
        "  [--mapping-folder] = specify alternative mapping folder\n\n"
    )

    @staticmethod
    def callback_function(
        source_path: str,
        target_path: str,
        target_format: str,
        mask_and_scale: None | bool,
        mapping_folder: None | str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """

        Parameters
        ----------
        source_path
        target_path
        target_format
        mask_and_scale
        mapping_folder

        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.convert")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Converting product {source_path} to {target_path}")
        logger.info(f"Target format {target_format}")
        if mask_and_scale is not None:
            logger.info(f"Mask and scale {mask_and_scale}")
        if mapping_folder is not None:
            EOConfiguration()["mapping__folder"] = mapping_folder
        try:
            _, name = convert(
                source_path=source_path,
                target_path=target_path,
                mask_and_scale=mask_and_scale,
                target_format=target_format,
            )
            logger.info(f"Converted to {name}")
        except Exception as e:
            logger.error("Error while converting product")
            logger.error(f"{e}")
            raise e

        logger.info(f"Product successfully written in {target_path}")
        return 0
