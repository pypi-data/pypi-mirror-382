from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn
from pytest_dataguard.plugin import DataGuardPlugin

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser


# NoReturn means the function does not return any value
def pytest_addoption(parser: Parser) -> NoReturn:
    # add a command line option to pytest
    group = parser.getgroup("pytest-dataguard")
    group.addoption(
        "--file",
        default="",
        action="store",
        help="Path to the CSV file to be validated",
    )
    group.addoption(
        "--not_null",
        action="store_true",
        default=False,
        help="Allow null values in the file (by default, nulls are not allowed)",
    )
    group.addoption(
        "--unique",
        default=[],
        action="append",
        help="Checks that there is no duplicate column in the file",
    )


def pytest_configure(config: Config) -> NoReturn:
    # register the plugin if the --file option is provided
    if not config.getoption("--file"):
        return

    pluginmanager = config.pluginmanager

    plugin = DataGuardPlugin(config)
    pluginmanager.register(plugin)
