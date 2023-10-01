import sys
from argparse import ArgumentParser
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
        usage="%(prog)s [options]",
        description="A Python command-line utility to discover updates for your Gradle version catalogs.",
        allow_abbrev=False,
        epilog="Visit project repository to get latest information."
    )
    parser.add_argument(
        "-p", "--catalog-path",
        type=str,
        dest="catalog_path",
        metavar="path",
        help="Path to gradle version catalog. If catalog path not provided script looking for version catalog in "
             "current directory.",
    )
    parser.add_argument(
        "-rp", "--repositories-path",
        type=str,
        dest="repositories_path",
        metavar="path",
        help="Path to .toml file with repositories info. If repositories path not provided script looking for "
             "repositories file in current directory.",
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
        version=f"%(prog)s 0.0.1",  # TODO: to be read from single-source
    )
    arguments = parser.parse_args()

    return KatalogerConfiguration(
        path_to_catalog=to_catalog_path(arguments.catalog_path),
        path_to_repositories=to_repositories_path(arguments.repositories_path),
        verbose=arguments.verbose,
        suggest_unstable_updates=arguments.suggest_unstable_updates,
        fail_on_updates=arguments.fail_on_updates,
    )


def to_catalog_path(path_string: Optional[str]) -> Path:
    if path_string:
        return convert_to_path(path_string)

    catalog_candidate = Path.cwd() / "libs.versions.toml"
    if not (catalog_candidate.exists() and catalog_candidate.is_file()):
        raise KatalogerConfigurationException("libs.version.toml not found in current directory. Please specify path "
                                              "to catalog with -p parameter.")

    return catalog_candidate


def to_repositories_path(path_string: Optional[str]) -> Path:
    if path_string:
        return convert_to_path(path_string)

    repositories_candidate = Path.cwd() / "default.repositories.toml"
    if not (repositories_candidate.exists() and repositories_candidate.is_file()):
        raise KatalogerConfigurationException("default.repositories.toml not found in current directory. Please specify"
                                              " path to repositories with -rp parameter.")

    return repositories_candidate


def convert_to_path(path_string: str) -> Path:
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
                           .set_repositories_path(Path(configuration.path_to_repositories))
                           .set_verbose(verbose=configuration.verbose)
                           .build())

        updates = await catalog_updater.get_catalog_updates(Path(configuration.path_to_catalog))
        for update in updates:
            print(update)

        if configuration.fail_on_updates:
            return min(1, len(updates))  # Non-zero return code if we found updates
        else:
            return 0

    try:
        return asyncio.run(async_main())
    except KatalogerException as error:
        print(f"Kataloger: {error.message}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
