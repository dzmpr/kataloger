from argparse import ArgumentParser
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import List, Optional

from kataloger import package_name
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.kataloger_arguments import KatalogerArguments
from kataloger.helpers.path_helpers import str_to_path


def parse_arguments(*args: str) -> KatalogerArguments:
    parser = ArgumentParser(
        prog="kataloger",
        description="A Python command-line utility to discover updates for your gradle version catalogs.",
        allow_abbrev=False,
        epilog="Visit project repository to get more information.",
    )
    parser.add_argument(
        "-p", "--path",
        action="append",
        dest="paths",
        help="Path(s) to gradle version catalog. If catalog path not provided script looking for "
             "version catalogs in current directory.",
    )
    parser.add_argument(
        "-c", "--configuration",
        type=str,
        dest="configuration_path",
        metavar="path",
        help="Path to .toml file with configuration. If path not provided script looking for "
             "default.configuration.toml file in current directory.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=None,
        dest="verbose",
        help="Enables detailed output.",
    )
    parser.add_argument(
        "-u", "--suggest-unstable",
        action="store_true",
        default=None,
        dest="suggest_unstable_updates",
        help="Allow %(prog)s suggest update from stable version to unstable.",
    )
    parser.add_argument(
        "-f", "--fail-on-updates",
        action="store_true",
        default=None,
        dest="fail_on_updates",
        help="Exit with non-zero code when at least one update found.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_kataloger_version()}",
    )
    arguments = parser.parse_args(args)

    return KatalogerArguments(
        configuration_path=_get_configuration_path(arguments.configuration_path),
        configuration_data=ConfigurationData(
            catalogs=_get_catalogs(arguments.paths),
            library_repositories=None,
            plugin_repositories=None,
            verbose=arguments.verbose,
            suggest_unstable_updates=arguments.suggest_unstable_updates,
            fail_on_updates=arguments.fail_on_updates,
        ),
    )


def _get_kataloger_version() -> str:
    if __name__ == "__main__":
        return "indev"

    try:
        return version(package_name)
    except PackageNotFoundError:
        return "unknown"


def _get_catalogs(path_strings: List[str]) -> Optional[List[Catalog]]:
    if path_strings:
        return [Catalog.from_path(str_to_path(path_string=path_str, root_path=Path.cwd())) for path_str in path_strings]

    return None


def _get_configuration_path(path_string: Optional[str]) -> Optional[Path]:
    if path_string:
        return str_to_path(path_string=path_string, root_path=Path.cwd())

    return None
