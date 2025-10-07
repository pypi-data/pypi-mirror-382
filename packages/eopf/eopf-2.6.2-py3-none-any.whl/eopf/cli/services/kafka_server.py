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
kafka_server.py

Kafka consumer service implementation

"""
import logging
import warnings
from typing import Any

import click
import yaml
from aiokafka import AIOKafkaConsumer

from eopf.cli.cli import EOPFPluginCommandCLI, async_cmd
from eopf.triggering.runner import EORunner

logger = logging.getLogger("eopf")


class EOKafkaServer(EOPFPluginCommandCLI):
    """EOKafkaRunner cli command to run a kafka message consumer

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "kafka-consumer"
    cli_params: list[click.Parameter] = [
        click.Option(
            ["--kafka-server"],
            default="127.0.0.1:9092",
            help="Kafka services information (default 127.0.0.1:9092)",
        ),
        click.Option(["--kafka-topic"], default="run", help="Kafka topic (default 'run')"),
    ]
    help = "Get and load_file messages from kafka an execute EOTrigger"

    @staticmethod
    @async_cmd
    async def callback_function(kafka_server: str, kafka_topic: str, *args: Any, **kwargs: Any) -> None:
        warnings.warn("Kafka call is deprecated, no guarantee to work", DeprecationWarning)
        """Run the EOTrigger.run for each message found in the topic"""
        consumer = AIOKafkaConsumer(kafka_topic, bootstrap_servers=kafka_server)
        await consumer.start()
        try:
            async for msg in consumer:
                logger.info(f"Consume message {msg} for {kafka_server}/{kafka_topic}")
                try:
                    EORunner().run(yaml.safe_load(msg.value))
                except Exception as e:
                    logger.exception(e)
        finally:
            await consumer.stop()
