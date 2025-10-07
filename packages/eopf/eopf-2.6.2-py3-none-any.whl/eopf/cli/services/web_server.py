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
web_server.py

HTTP sync service implementation

"""
import logging
import sys
import traceback
from typing import Any

import click
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import Receive, Scope, Send

from eopf.cli.cli import EOPFPluginCommandCLI
from eopf.triggering.runner import EORunner

logger = logging.getLogger("eopf")


class EOWebServer(FastAPI, EOPFPluginCommandCLI):
    """EOWebServer cli command to run a web services

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name = "web-services"
    cli_params: list[click.Parameter] = [
        click.Option(["--host"], default="127.0.0.1", help="host information (default 127.0.0.1)"),
        click.Option(["--port"], default=8080, help="Port (default 8080)"),
        click.Option(["--log-level"], default="info"),
    ]
    help = "Run web services to run EOTrigger with post payload"

    def __init__(self) -> None:
        FastAPI.__init__(self)
        EOPFPluginCommandCLI.__init__(self)
        self.add_api_route("/run", self.run_request, methods=["POST"])

    @staticmethod
    async def run_request(request: Request) -> JSONResponse:
        """API route provide a simple way to execute EOTrigger.run

        Parameters
        ----------
        request: Request
            post information (should be json data)

        Returns
        -------
        JSONResponse
            if "err" is provide, an error as occur
        """
        try:
            payload_json = await request.json()
            logger.info(f"Triggered with {payload_json}")
            EORunner().run(payload_json)
        except Exception as e:
            logger.exception(e)

            *_, exc_traceback = sys.exc_info()
            return JSONResponse(content={"err": "\n".join(traceback.format_tb(exc_traceback))}, status_code=200)
        return JSONResponse(content={}, status_code=200)

    @staticmethod
    def callback_function(host: str, port: int, log_level: str, *args: Any, **kwargs: Any) -> None:
        """Start a web services with the given information

        Parameters
        ----------
        host: str
            On which IP/host name should start
        port: int
            On which port start
        log_level: str
            base level information
        """
        uvicorn.run(EOWebServer(), host=host, port=port, log_level=log_level)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await FastAPI.__call__(self, scope, receive, send)
