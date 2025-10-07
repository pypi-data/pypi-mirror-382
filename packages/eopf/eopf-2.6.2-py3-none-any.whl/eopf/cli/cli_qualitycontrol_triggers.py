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
cli_qualitycontrol_triggers.py

QualityControl CLI command implementation


"""
from typing import Any, List, Optional

import click

from eopf import EOZarrStore, OpeningMode, __version__
from eopf.cli.cli import EOPFPluginCommandCLI, EOPFPluginGroupCLI
from eopf.common.file_utils import AnyPath
from eopf.logging import EOLogging
from eopf.qualitycontrol.eo_qc_processor import EOQCProcessor


class EOCLIQualityControlCheckTrigger(EOPFPluginCommandCLI):
    """EOTrigger cli command to apply check on a product.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "check"
    cli_params: list[click.Parameter] = [
        click.Argument(["product_path"], type=click.Path()),
        click.Option(["--output-product"], type=click.Path()),
        click.Option(["--output-report"], type=click.Path()),
        click.Option(["--config-folder"], type=click.Path()),
        click.Option(["--add-config-folder"], type=click.Path()),
    ]
    help = (
        "Request the OLQC check on zarr eoproduct\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  product_path = Path to the zarr eoproduct\n\n"
        "  [--output-product] = Product to write the result to, if not not written\n\n"
        "  [--output-report] = Report to write to, if not not written\n\n"
        "  [--config-folder] = Base config folder,  if not default used\n\n"
        "  [--add-config-folder] = Additional config folder to use\n\n"
    )

    @staticmethod
    def callback_function(
        product_path: str,
        output_product: None | str,
        output_report: None | str,
        config_folder: None | str,
        add_config_folder: None | str,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """

        Parameters
        ----------
        product_path
        output_product
        output_report
        config_folder
        add_config_folder

        Returns
        -------

        """

        logger = EOLogging().get_logger()
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Checking product  {product_path}")
        if output_product is None and output_report is None:
            logger.error("Need at least one of output_product or output_report")
            return 1
        if config_folder is None and add_config_folder is None:
            config_folders: Optional[List[str | AnyPath]] = None
        else:
            config_folders = []
            if config_folder is not None:
                config_folders.append(config_folder)
            if add_config_folder is not None:
                config_folders.append(add_config_folder)

        eoqc_processor = EOQCProcessor(
            config_folders=config_folders,
            update_attrs=(output_product is not None),
            report_path=output_report,
        )
        inproduct = EOZarrStore(url=product_path).load()
        eoqc_processor.check(inproduct)
        if output_product is not None:
            with EOZarrStore(url=output_product).open(mode=OpeningMode.CREATE) as store:
                store[""] = inproduct

        return 0


class EOCLIQualityControlTrigger(EOPFPluginGroupCLI):
    """EOTrigger cli command aggregator to quality control triggers

    Parameters
    ----------
    **attrs: Any
        any argument for click.Command, click.MultiCommand

    See Also
    --------
    click.Group
    """

    name = "qualitycontrol"
    cli_commands: list[click.Command] = [
        EOCLIQualityControlCheckTrigger(),
    ]
    help = "CLI commands to run EOQC processor"
