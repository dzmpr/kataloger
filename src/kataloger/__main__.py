import sys
from argparse import ArgumentParser
from importlib.metadata import version
from importlib.resources import files, as_file
from pathlib import Path
from typing import Optional

import asyncio

from kataloger.catalog_updater_builder import CatalogUpdaterBuilder
from kataloger.data.kataloger_configuration import KatalogerConfiguration
from kataloger.execptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.execptions.kataloger_exception import KatalogerException
from kataloger.update_resolver.universal.universal_update_resolver import UniversalUpdateResolver
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


def parse_arguments() -> KatalogerConfiguration:
    parser = ArgumentParser(
        prog="kataloger",
        description="A Python command-line utility to discover updates for your gradle version catalogs.",
        allow_abbrev=False,
        epilog="Visit project repository to get more information."
    )
    parser.add_argument(
        "-p", "--path",
        action="append",
        dest="paths",
        help="Path(s) to gradle version catalog. If catalog path not provided script looking for version catalogs in "
             "current directory.",
    )
    parser.add_argument(
        "-rp", "--repositories-path",
        type=str,
        dest="repositories_path",
        metavar="path",
        help="Path to .toml file with repositories info. If repositories path not provided script looking for "
             "default.repositories.toml file in current directory.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        help="Enables detailed output.",
    )
    parser.add_argument(
        "-u", "--suggest-unstable",
        action="store_true",
        dest="suggest_unstable_updates",
        help="Allow %(prog)s suggest update from stable version to unstable.",
    )
    parser.add_argument(
        "-f", "--fail-on-updates",
        action="store_true",
        dest="fail_on_updates",
        help="Exit with non-zero code when at least one update found.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_kataloger_version()}",
    )
    arguments = parser.parse_args()

    return KatalogerConfiguration(
        catalogs=get_catalog_paths(arguments.paths),
        repositories_path=get_repositories_path(arguments.repositories_path),
        verbose=arguments.verbose,
        suggest_unstable_updates=arguments.suggest_unstable_updates,
        fail_on_updates=arguments.fail_on_updates,
    )


def get_kataloger_version() -> str:
    if __name__ == '__main__':
        return "indev"
    else:
        return version(__package__ or __name__)


def get_catalog_paths(path_strings: list[str]) -> list[Path]:
    if path_strings:
        return list(map(lambda path: str_to_path(path), path_strings))

    # If catalog path not provided try to find catalogs in cwd.
    catalog_files = Path.cwd().glob("*.versions.toml")
    catalog_paths = list(filter(lambda path: path.exists() and path.is_file(), catalog_files))
    if not catalog_paths:
        raise KatalogerConfigurationException("Gradle version catalog not found in current directory. Please specify "
                                              "path to catalog via parameter or run tool from directory with catalog.")

    return catalog_paths


def get_repositories_path(path_string: Optional[str]) -> Path:
    if path_string:
        return str_to_path(path_string)

    repositories_candidate = Path.cwd() / "default.repositories.toml"
    if repositories_candidate.exists() and repositories_candidate.is_file():
        return repositories_candidate

    with as_file(files("kataloger").joinpath("default.repositories.toml")) as path:
        bundled_repositories_path = path
    return bundled_repositories_path


def str_to_path(path_string: str) -> Path:
    path = Path(path_string)
    if not (path.exists() or path.is_file()):
        raise KatalogerConfigurationException(message=f"Incorrect path: {path_string}.")

    return path


def main() -> int:
    async def async_main():
        configuration = parse_arguments()

        update_resolver = UniversalUpdateResolver(
            version_factories=[UniversalVersionFactory()],
            suggest_unstable_updates=configuration.suggest_unstable_updates,
        )

        catalog_updater = (CatalogUpdaterBuilder()
                           .add_resolver(update_resolver)
                           .set_repositories_path(configuration.repositories_path)
                           .set_verbose(verbose=configuration.verbose)
                           .build())

        has_updates = False
        for catalog_path in configuration.catalogs:
            updates = await catalog_updater.get_catalog_updates(catalog_path)
            if not has_updates and updates:
                has_updates = True

            if len(configuration.catalogs) > 1 and updates:
                if catalog_path.name.endswith(".versions.toml"):
                    catalog_name = catalog_path.name.removesuffix(".versions.toml")
                else:
                    catalog_name = catalog_path.name
                print(f"Updates for \"{catalog_name}\" catalog.")
            for update in updates:
                print(update)
            if len(configuration.catalogs) > 1 and updates:
                print("")

        if configuration.fail_on_updates and has_updates:
            return 1
        else:
            return 0

    try:
        return asyncio.run(async_main())
    except KatalogerException as error:
        print(f"Kataloger: {error.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
