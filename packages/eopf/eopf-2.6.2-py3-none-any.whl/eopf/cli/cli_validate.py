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
cli_validate.py

CLI command to validate products


"""

from typing import Any, Optional

import click

from eopf import EOContainer, EOProduct, __version__
from eopf.cli.cli import EOPFPluginCommandCLI
from eopf.common.file_utils import AnyPath
from eopf.common.functions_utils import parse_flag_expr
from eopf.logging import EOLogging
from eopf.product import eo_container_validation, eo_product_validation
from eopf.product.eo_validation import AnomalyDescriptor, ValidationMode
from eopf.store.store_factory import EOStoreFactory


class EOCLIValidate(EOPFPluginCommandCLI):
    """EO cli command to validate a product.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "validate"
    cli_params: list[click.Parameter] = [
        click.Argument(["source_path"], type=click.Path()),
        click.Option(["--mode"], type=str),
    ]
    help = (
        "Validate a product\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  source_path = Source product to validate (SAFE/ZARR) \n\n"
        "  [--mode] = mode to use to validate\n\n"
    )

    @staticmethod
    def callback_function(source_path: str, mode: Optional[str], *args: Any, **kwargs: Any) -> Any:
        """

        Parameters
        ----------
        source_path
        mode

        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.validate")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Validate product {source_path}")
        if mode is not None:
            validation_mode = parse_flag_expr(mode, ValidationMode)
        else:
            validation_mode = ValidationMode.STAC | ValidationMode.STRUCTURE | ValidationMode.MODEL

        logger.info(f"Using mode : {validation_mode}")
        source_fspath: AnyPath = AnyPath.cast(url=source_path)

        # determine the source store
        source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)
        # load the EOProduct from source_path
        source_store = source_store_class(source_fspath.path)
        source_store.open()
        eop: EOProduct | EOContainer = source_store.load()
        source_store.close()

        logger.info(f"EO {eop.name} successfully loaded, starting to validate")
        anomalies: list[AnomalyDescriptor] = []

        if isinstance(eop, EOProduct):
            flag, anomalies = eo_product_validation.is_valid_product(eop, validation_mode=validation_mode)
        elif isinstance(eop, EOContainer):
            flag, anomalies = eo_container_validation.is_valid_container(eop, validation_mode=validation_mode)

        if len(anomalies) != 0:
            logger.error(f"Product {eop.name} is not valid !!!")
        else:
            logger.info(f"Product {eop.name} is valid")
        for anom in anomalies:
            logger.error(f"** {anom.description}")
        if len(anomalies) != 0:
            raise click.ClickException(f"Product {eop.name} is not valid !!!")

        return 0
