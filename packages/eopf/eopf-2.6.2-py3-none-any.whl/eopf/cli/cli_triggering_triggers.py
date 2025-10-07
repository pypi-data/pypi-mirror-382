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
cli_triggering_trigger.py

Triggering CLI command implementation


"""
import importlib
import json
import sys
import urllib.parse as urlparser
import warnings
from pprint import pformat
from typing import Any

import click
import requests
import yaml

from eopf import EOConfiguration, __version__
from eopf.cli.cli import (
    EOPFPluginCommandCLI,
    EOPFPluginGroupCLI,
    async_cmd,
    click_callback,
)
from eopf.exceptions.errors import ExceptionWithExitCode
from eopf.logging import EOLogging
from eopf.triggering.runner import EORunner


@click_callback
def load_yaml_file(file_name: str) -> dict[str, Any]:
    """Wrap yaml load_file to automatically load_file from a filename in click.Command

    Parameters
    ----------
    file_name: str
        name of the file to load_file the yaml content

    Returns
    -------
    dict[str, Any]
    """
    with open(file_name, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for key in ["workflow", "breakpoints", "I/O", "dask_context"]:
        if isinstance(data.get(key), str):
            data[key] = load_yaml_file(data[key])
    return data


@click_callback
def format_server_info(value: Any) -> str:
    """Wrap urlparse to automatically format url with trigger endpoint

    Parameters
    ----------
    value: str
        url to the target web server

    Returns
    -------
    str
    """
    url = urlparser.urlparse(value)
    if not url.path.endswith("/run"):
        url = urlparser.urlparse(f"{url.geturl()}/run")
    return url.geturl()


class EOTaskTableCLITrigger(EOPFPluginCommandCLI):
    """EOTrigger cli command to get tasktable info for a processor.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "tasktable"
    cli_params: list[click.Parameter] = [
        click.Argument(["module_name"]),
        click.Argument(
            ["pu_name"],
        ),
        click.Option(["--output-file"], type=click.Path()),
        click.Option(["--mode"]),
        click.Option(["--list-mode"], is_flag=True, flag_value=True),
        click.Option(["--list-params"], is_flag=True, flag_value=True),
    ]
    help = (
        "Request the tasktable description from module_name/pu_name\n\n\n"
        f"CPM Version {__version__}\n\n"
        "Args:\n\n"
        "  module_name = python module to load the ProcessingUnit from\n\n"
        "  pu_name = python ProcessingUnit\n\n"
        "  --output-file = File to write tasktable to\n\n"
        "  --mode = Processing mode to request the tasktable\n\n"
        "  --list-mode = List the available mode for the ProcessingUnit and exit ( no Tasktable in this case)\n\n"
        "  --list-params = List the parameters for the ProcessingUnit and exit ( no Tasktable in this case)\n\n"
    )

    @staticmethod
    def callback_function(
        *args: Any,
        module_name: str,
        pu_name: str,
        output_file: None | str,
        mode: None | str,
        list_mode: None | bool,
        list_params: None | bool,
        **kwargs: Any,
    ) -> Any:
        """

        Parameters
        ----------
        list_params
        pu_name
        list_mode
        mode
        module_name
        output_file
        """

        logger = EOLogging().get_logger()
        logger.info(f"CPM Version {__version__}")
        logger.info(f"Retrieving TaskTable for  {module_name}.{pu_name}")
        try:
            module = importlib.import_module(module_name)
            try:
                unit_class = getattr(module, pu_name)
            except AttributeError:
                logger.error(f"Class {pu_name} not found in module {module_name} for workflow")
                sys.exit(1)
        except (
            ImportError,
            ModuleNotFoundError,
            SyntaxError,
            AttributeError,
            PermissionError,
            ValueError,
            TypeError,
            OSError,
            NameError,
        ) as e:
            logger.error(f"Error while importing module {module_name} : {type(e)} {e}")
            sys.exit(1)
        if list_mode:
            modes_str = ", ".join(unit_class.get_available_modes())
            logger.info(f"Available modes: {modes_str}")
            logger.info(f"Default mode: {unit_class.get_default_mode()}")
            return 0
        if list_params:
            logger.info("\n\n" + pformat(EOConfiguration().requested_params_description()))
            return 0
        mode = mode if mode else unit_class.get_default_mode()
        if output_file is not None:
            with open(output_file, "w+", encoding="utf-8") as f:
                json.dump(unit_class.get_tasktable_description(mode), f)
        logger.info(unit_class.get_tasktable_description(mode))

        return 0


class CustomClickException(click.ClickException):
    def __init__(self, message: str, exit_code: int = 3) -> None:
        super().__init__(message)
        self.exit_code: int = exit_code  # Must be set after super().__init__()


class EOLocalCLITrigger(EOPFPluginCommandCLI):
    """EOTrigger cli command to run locally an EOProcessingUnit from a specific
    json file.

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "local"
    cli_params: list[click.Parameter] = [
        click.Argument(
            ["yaml-data-file"],
            type=click.Path(exists=True, file_okay=True, dir_okay=False),
            callback=load_yaml_file,
        ),
    ]
    help = "Trigger a specific EOProcessingUnit locally from the given json data"

    @staticmethod
    def callback_function(yaml_data_file: dict[str, Any], *args: Any, **kwargs: Any) -> Any:
        """Run the EOTrigger.run with the json data

        Parameters
        ----------
        yaml_data_file: dict
            json data used as payload
        """

        logger = EOLogging().get_logger("eopf.trigger.local")
        logger.info(f"CPM Version {__version__}")
        logger.info(f"RUN with {yaml_data_file}")
        exit_code = 0
        runner = EORunner()
        try:
            runner.run(yaml_data_file)
        except ExceptionWithExitCode as err:
            logger.error(f"Error running {yaml_data_file} : {err}")
            exit_code = err.exit_code

            raise CustomClickException(f"{type(err).__name__}: {str(err)}", exit_code=exit_code) from err
        except Exception as err:
            logger.error(f"Error running {yaml_data_file} : {err}")
            raise
        return exit_code


class EORequestCLITrigger(EOPFPluginCommandCLI):
    """EOTrigger cli command to trigger web services from a json file

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "request"
    cli_params: list[click.Parameter] = [
        click.Argument(
            ["yaml-data-file"],
            type=click.Path(exists=True, file_okay=True, dir_okay=False),
            callback=load_yaml_file,
        ),
        click.Option(
            ["--server-info"],
            default="http://127.0.0.1:8080",
            callback=format_server_info,
            help="target server (default: http://127.0.0.1:8080)",
        ),
    ]
    help = "Trigger a specific EOProcessingUnit on the target web server from the given json data"

    @staticmethod
    def callback_function(yaml_data_file: dict[str, Any], server_info: str, *args: Any, **kwargs: Any) -> None:
        """Send the request to the web service to trigger EOTrigger.run*

        Parameters
        ----------
        yaml_data_file: dict
            yaml data used as payload
        server_info: str
            target server information, must start with scheme
        """
        r = requests.post(url=server_info, json=yaml.safe_dump(yaml_data_file), timeout=60)
        click.echo(f"Server return status code {r.status_code} with content: {r.content}")


class EOKafkaCLITrigger(EOPFPluginCommandCLI):
    """EOTrigger cli command to send data from a json file to kafka services

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "kafka"
    cli_params: list[click.Parameter] = [
        click.Argument(
            ["yaml-data-file"],
            type=click.Path(exists=True, file_okay=True, dir_okay=False),
            callback=load_yaml_file,
        ),
        click.Option(
            ["--kafka-server"],
            default="127.0.0.1:9092",
            help="Kafka server information (default 127.0.0.1:9092)",
        ),
        click.Option(["--kafka-topic"], default="run", help="Kafka topic (default 'run')"),
    ]
    help = "Trigger a specific EOProcessingUnit on the target kafka server from the given json data"

    @staticmethod
    @async_cmd
    async def callback_function(
        yaml_data_file: dict[str, Any],
        kafka_server: str,
        kafka_topic: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Send the request to kafka service to triggers EOTrigger.run

        Parameters
        ----------
        yaml_data_file: dict
            yaml data used as payload
        kafka_server: str
            target services information
        kafka_topic: str
            target topic
        """
        warnings.warn("Kafka call is deprecated, no guarantee to work", DeprecationWarning)
        from aiokafka import AIOKafkaProducer

        producer = AIOKafkaProducer(bootstrap_servers=kafka_server)
        await producer.start()
        try:
            msg = await producer.send_and_wait(kafka_topic, yaml.dump(yaml_data_file).encode())
        finally:
            await producer.stop()
        click.echo(f"{msg}")


class EOCLITriggeringTrigger(EOPFPluginGroupCLI):
    """EOTrigger cli command aggregator to triggers other services

    Parameters
    ----------
    **attrs: Any
        any argument for click.Command, click.MultiCommand

    See Also
    --------
    click.Group
    """

    name = "trigger"
    cli_commands: list[click.Command] = [
        EOTaskTableCLITrigger(),
        EOLocalCLITrigger(),
        EORequestCLITrigger(),
        EOKafkaCLITrigger(),
    ]
    help = f"CLI commands to trigger EOProcessingUnit\n\n\nCPM Version {__version__}\n\n"
