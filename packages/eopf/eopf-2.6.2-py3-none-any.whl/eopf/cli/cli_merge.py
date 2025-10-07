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
cli_merge.py

Merging CLI command implementation


"""
from typing import Any

import click
from zarr.errors import ContainsGroupError

import eopf.computing.merge
from eopf import __version__
from eopf.cli.cli import EOPFPluginCommandCLI
from eopf.logging import EOLogging


class EOCLIMerge(EOPFPluginCommandCLI):
    """EO cli command to Merge L1C/L2A S2 products.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "merge"
    cli_params: list[click.Parameter] = [
        click.Argument(["products_path"], type=click.Path()),
        click.Argument(["output_product"], type=click.Path()),
        click.Option(["--recompute-attrs"], is_flag=True, flag_value=True),
        click.Option(["--sanity-check"], is_flag=True, flag_value=True),
        click.Option(["--allow-missing-tiles"], is_flag=True, flag_value=True),
        click.Option(["--overwrite"], is_flag=True, flag_value=True),
    ]
    help = (
        "Merge multiples S2 L1C or S2 L2A products into a single one\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  products_path = Directory to the zarrs eoproducts\n\n"
        "  output_product = Product to write the result to\n\n"
        "  [--recompute-attrs] = Do recompute attrs\n\n"
        "  [--sanity-check] = Do a quality check on the result\n\n"
        "  [--allow-missing-tiles] = Allow for missing tiles, will be filled with 0\n\n"
        "  [--overwrite] = Allows overwriting an existing output product\n\n"
    )

    @staticmethod
    def callback_function(
        products_path: str,
        output_product: str,
        recompute_attrs: None | bool,
        sanity_check: None | bool,
        allow_missing_tiles: None | bool,
        overwrite: None | bool,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """

        Parameters
        ----------
        products_path
        output_product
        recompute_attrs
        sanity_check
        allow_missing_tiles
        overwrite

        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.merge")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Merging products in {products_path} to {output_product}")

        if allow_missing_tiles:
            logger.info("Missing tiles authorized")

        try:
            dt = eopf.computing.merge.open_and_combine_tiles(
                input_dir=products_path,
                allow_missing_tiles=allow_missing_tiles if allow_missing_tiles is not None else False,
                update_mode=recompute_attrs if recompute_attrs is not None else False,
            )
            dt.to_zarr(output_product, mode="w" if overwrite else "w-")
        except ContainsGroupError as e:
            logger.error(
                f"Products most likely already exists in {output_product}, either use --overwrite or delete it",
            )
            logger.error(e)
            return 1
        except ValueError as e:
            logger.error("Error while merging tiles; try with --allow-missing-tiles option")
            logger.error(e)
            return 1

        if sanity_check:
            logger.info("Sanity check activated")
            eopf.computing.merge.sanity_check(products_path, dt)

        logger.info(f"Product successfully written in {output_product}")
        return 0
