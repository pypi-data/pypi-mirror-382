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
cli_model.py

CLI command to request/validate pydantic models


"""
from logging import Logger
from typing import Any, Optional

import click

from eopf import EOConfiguration, EOContainer, EOProduct, __version__
from eopf.cli.cli import EOPFPluginCommandCLI, EOPFPluginGroupCLI
from eopf.common.file_utils import AnyPath, load_json_file
from eopf.exceptions.errors import ExceptionWithExitCode
from eopf.logging import EOLogging
from eopf.product.eo_container_validation import (
    EOContainerModel,
    check_container_model_validity,
    container_to_model_json_file,
    validate_container_against_model,
)
from eopf.product.eo_product_validation import (
    EOProductModel,
    check_product_model_validity,
    product_to_model_json_file,
    validate_product_against_model,
)
from eopf.product.eo_validation import AnomalyDescriptor
from eopf.store.store_factory import EOStoreFactory


class EOCLIModelCreate(EOPFPluginCommandCLI):
    """EO cli command to create a model from a zarr product.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    help = "CPM Command line tools\n\nCPM Version {__version__}\n\nExtra info here"
    name = "create"
    cli_params: list[click.Parameter] = [
        click.Argument(["source_path"], type=click.Path()),
        click.Option(["--target_path"], type=click.Path()),
    ]
    help = (
        "Generate the json model of a product\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  source_path = Source product \n\n"
        "  [target_path] = json file to write to, if not provided will take the product_type.json along the product\n\n"
    )

    @staticmethod
    def callback_function(source_path: str, target_path: Optional[str], *args: Any, **kwargs: Any) -> Any:
        """

        Parameters
        ----------
        source_path
        target_path



        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.model_create")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Creating model for product {source_path}")

        try:
            source_fspath: AnyPath = AnyPath.cast(url=source_path)

            # determine the source store
            source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)
            # load the EOProduct from source_path
            source_store = source_store_class(source_fspath.path)
            source_store.open()
            eop: EOProduct | EOContainer = source_store.load()

            source_store.close()

            logger.info(f"EO {eop} successfully loaded, starting to write json model")

            if isinstance(eop, EOProduct):
                target_fspath = (
                    AnyPath.cast(target_path)
                    if target_path is not None
                    else source_fspath.dirname() / eop.product_type + ".json"
                )
                product_to_model_json_file(eop, target_fspath)
            elif isinstance(eop, EOContainer):
                target_fspath = (
                    AnyPath.cast(target_path)
                    if target_path is not None
                    else source_fspath.dirname() / eop.container_type + ".json"
                )
                container_to_model_json_file(eop, target_fspath)

        except Exception as e:
            logger.error("Error while generating product model")
            logger.error(f"{e}")
            raise click.ClickException("Error while generating product model")

        logger.info("Model successfully written")
        return 0


class EOCLIModelValidate(EOPFPluginCommandCLI):
    """EO cli command to create a model from a zarr product.

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
        click.Option(["--model_path"], type=click.Path()),
    ]
    help = (
        "Validate a product against its model\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  source_path = Source product \n\n"
        "  [model_path] = json file to read model from, if not provided takes the official ones\n\n"
    )

    @staticmethod
    def callback_function(source_path: str, model_path: Optional[str], *args: Any, **kwargs: Any) -> Any:
        """

        Parameters
        ----------
        source_path
        model_path



        Returns
        -------

        """

        logger = EOLogging().get_logger("eopf.cli.model_validate")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Validation product {source_path}")
        if model_path is not None:
            logger.info(f"Using model file {model_path}")
        else:
            logger.info(f"Using official models in : {EOConfiguration().model__folder}")
        try:
            source_fspath: AnyPath = AnyPath.cast(url=source_path)

            # determine the source store
            source_store_class = EOStoreFactory.get_product_store_by_file(source_fspath)
            # load the EOProduct from source_path
            source_store = source_store_class(source_fspath.path)
            source_store.open()
            eop: EOProduct | EOContainer = source_store.load()
            source_store.close()

            logger.info(f"EO {eop.name} successfully loaded, starting to validate model")
            anomalies: list[AnomalyDescriptor] = []

            if isinstance(eop, EOProduct):
                EOCLIModelValidate._validate_product(anomalies, eop, logger, model_path)
            elif isinstance(eop, EOContainer):
                EOCLIModelValidate._validate_container(anomalies, eop, logger, model_path)
            if len(anomalies) != 0:
                logger.error(f"Product {eop.name} is not valid against it's model")
            else:
                logger.info(f"Product {eop.name} is valid against it's model !!!")
            for anom in anomalies:
                logger.error(f"** {anom.description}")
            if len(anomalies) != 0:
                raise ExceptionWithExitCode(f"Product {eop.name} is not valid against it's model !!!")
        except ExceptionWithExitCode as e:
            raise e
        except Exception as e:
            logger.error("Error while validating product against model")
            logger.error(f"{e}")
            raise ExceptionWithExitCode("Error while validating product against model", exit_code=1) from e

        return 0

    @staticmethod
    def _validate_container(
        anomalies: list[AnomalyDescriptor],
        eop: EOContainer,
        logger: Logger,
        model_path: str | None,
    ) -> None:
        if model_path:
            json_path = AnyPath(model_path)
            data = load_json_file(json_path)
            loadedc = EOContainerModel(**data)
            validate_container_against_model(
                eop,
                out_anomalies=anomalies,
                logger=logger,
                model=loadedc,
                mode="EXACT",
            )
        else:
            check_container_model_validity(eop, out_anomalies=anomalies, logger=logger, check_submodels=False)

    @staticmethod
    def _validate_product(
        anomalies: list[AnomalyDescriptor],
        eop: EOProduct,
        logger: Logger,
        model_path: str | None,
    ) -> None:
        if model_path:
            json_path = AnyPath(model_path)
            data = load_json_file(json_path)
            loaded = EOProductModel(**data)
            validate_product_against_model(
                eop,
                out_anomalies=anomalies,
                logger=logger,
                model=loaded,
                mode="EXACT",
            )
        else:
            check_product_model_validity(eop, out_anomalies=anomalies, logger=logger)


class EOCLIModel(EOPFPluginGroupCLI):
    """EOTrigger cli command aggregator to triggers other services

    Parameters
    ----------
    **attrs: Any
        any argument for click.Command, click.MultiCommand

    See Also
    --------
    click.Group
    """

    name = "model"
    cli_commands: list[click.Command] = [EOCLIModelCreate(), EOCLIModelValidate()]
    help = f"CLI commands for pydantic model handlings\n\nCPM Version {__version__}\n\n"
