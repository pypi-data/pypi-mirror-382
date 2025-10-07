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
"""eopf.cli define abstracts classes to add new commands over eopf-cpm cli command."""

import asyncio
import importlib
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Coroutine, Optional

import click

from eopf import __version__


class EOPFPluginCommandCLI(ABC, click.Command):
    """Abstract class used to extend eopf cli and provide other commands

    Parameters
    ----------
    context_settings: dict, optional
        default values provide to click

    See Also
    --------
    click.Command
    """

    name: str
    cli_params: list[click.Parameter] = []
    """all argument and option associated to this command"""
    help: str = f"CPM Command line tools\n\nCPM Version {__version__}"
    """text used to specify to the user what this command is made for"""
    short_help: str = ""
    """shorter version of the help part"""
    epilog: str = ""
    """like help, but only provide at the end of the help command"""
    enable_help_option: bool = True
    """indicate if the help option is provide automatically (default True)"""
    hidden: bool = False
    """indicate if this command is hidden when it's search (default False)"""
    deprecated: bool = False
    """indicate if this command is deprecated or not (default False)"""

    def __init__(
        self,
        context_settings: Optional[dict[str, Any]] = None,
        options_metavar: Optional[str] = "[OPTIONS]",
    ) -> None:
        super().__init__(
            self.name,
            context_settings=context_settings,
            callback=self.callback_function,
            params=self.cli_params,
            help=self.help,
            epilog=self.epilog,
            short_help=self.short_help,
            options_metavar=options_metavar,
            add_help_option=self.enable_help_option,
            no_args_is_help=self._no_args_is_help,
            hidden=self.hidden,
            deprecated=self.deprecated,
        )

    @staticmethod
    @abstractmethod
    def callback_function(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        """Abstract method to provide an interface for the logic to implement in this command"""

    @property
    def _no_args_is_help(self) -> bool:
        return any(isinstance(param, click.Argument) for param in self.cli_params)


class EOPFPluginGroupCLI(click.Group):
    """Abstract class used to extend eopf cli and provide other group of command

    Parameters
    ----------
    **attrs: Any
        any argument for click.Command, click.MultiCommand

    See Also
    --------
    click.Group
    """

    name: str
    cli_commands: list[click.Command] = []
    """Sequence of command aggregate here"""
    help: str = f"CPM Command line tools\n\nCPM Version {__version__}"
    """text used to specify to the user what this command is made for"""
    short_help: str = ""
    """shorter version of the help part"""
    epilog: str = ""
    """like help, but only provide at the end of the help command"""
    enable_help_option: bool = True
    """indicate if the help option is provide automatically (default True)"""
    hidden: bool = False
    """indicate if this command is hidden when it is searched (default False)"""
    deprecated: bool = False
    """indicate if this command is deprecated or not (default False)"""

    def __init__(self, **attrs: Any) -> None:
        super().__init__(
            self.name,
            self.cli_commands,
            help=self.help,
            epilog=self.epilog,
            short_help=self.short_help,
            add_help_option=self.enable_help_option,
            hidden=self.hidden,
            deprecated=self.deprecated,
            **attrs,
        )


class EOPFCLI(click.MultiCommand):
    """Command provided by the eopf cli and aggregate all sub command

    Sub Command are defined in the entry point 'eopf.cli' section.

    Examples
    --------
    [project.entry-points."eopf.cli"]
    my-cmd = "pkg.module.class_name"
    """

    def list_commands(self, ctx: click.Context) -> list[str]:
        return sorted(resource.name for resource in importlib.metadata.entry_points(group="eopf.cli"))

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        cmd = None
        for resource in importlib.metadata.entry_points(group="eopf.cli", name=cmd_name):
            cmd = resource.load()()
        return cmd


@click.command(
    name="eopf",
    cls=EOPFCLI,
    add_help_option=True,
    help=f"CPM Command line tools\n\nCPM Version {__version__}\n\n",
)
@click.version_option(
    version=__version__,  # will print your eopf.__version__
    prog_name="eopf-cpm",  # optional: defaults to command name
    message="%(prog)s %(version)s",  # optional custom format
)
def eopf_cli() -> None:  # pragma: no cover
    ...


def async_cmd(func: Callable[..., Any]) -> Callable[..., Coroutine[None, Any, Any]]:
    """Decorator to use click and async function / method"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Coroutine[None, Any, Any]:
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def click_callback(func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap function to be call by click callback directly"""

    def wrapper(ctx: click.Context, param: click.Parameter, value: Any) -> Any:
        if value is not None:
            return func(value)
        return None

    return wrapper
