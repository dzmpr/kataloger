import sys
from pathlib import Path
from typing import List, Optional, Tuple, TypeVar

from kataloger.cli.argument_parser import parse_arguments
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.kataloger_arguments import KatalogerArguments
from kataloger.data.kataloger_configuration import KatalogerConfiguration
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.helpers.backport_helpers import get_package_file
from kataloger.helpers.path_helpers import file_exists
from kataloger.helpers.toml_parse_helpers import load_configuration

T = TypeVar("T")


def merge(
    first: Optional[T],
    second: Optional[T],
    default: T,
) -> T:
    if first:
        return first
    if second:
        return second

    return default


def get_configuration() -> KatalogerConfiguration:
    arguments: KatalogerArguments = parse_arguments(*sys.argv[1:])
    args_cd: ConfigurationData = arguments.configuration_data
    conf_cd: ConfigurationData = load_configuration_data(arguments.configuration_path)

    catalogs: List[Catalog] = get_catalogs(args_cd.catalogs, conf_cd.catalogs)
    library_repositories: List[Repository]
    plugin_repositories: List[Repository]
    library_repositories, plugin_repositories = get_repositories(
        arg_library_repositories=args_cd.library_repositories,
        arg_plugin_repositories=args_cd.plugin_repositories,
        conf_library_repositories=conf_cd.library_repositories,
        conf_plugin_repositories=conf_cd.plugin_repositories,
    )

    return KatalogerConfiguration(
        catalogs=catalogs,
        library_repositories=library_repositories,
        plugin_repositories=plugin_repositories,
        verbose=merge(args_cd.verbose, conf_cd.verbose, default=False),
        suggest_unstable_updates=merge(
            args_cd.suggest_unstable_updates,
            conf_cd.suggest_unstable_updates,
            default=False,
        ),
        fail_on_updates=merge(args_cd.fail_on_updates, conf_cd.fail_on_updates, default=False),
    )


def get_catalogs(arg_catalogs: Optional[List[Catalog]], conf_catalogs: Optional[List[Catalog]]) -> List[Catalog]:
    if arg_catalogs:
        return arg_catalogs

    if conf_catalogs:
        return conf_catalogs

    # If catalogs not provided via command line arguments or specified in configuration trying to find them in cwd.
    cwd_catalogs: Optional[List[Catalog]] = find_cwd_catalogs()
    if cwd_catalogs:
        return cwd_catalogs

    message = ("Gradle version catalog not found in current directory. "
               "Please specify path to catalog via parameter, in configuration "
               "file or run tool from directory with catalog (*.versions.toml) file.")
    raise KatalogerConfigurationException(message)


def get_repositories(
    arg_library_repositories: Optional[List[Repository]],
    arg_plugin_repositories: Optional[List[Repository]],
    conf_library_repositories: Optional[List[Repository]],
    conf_plugin_repositories: Optional[List[Repository]],
) -> Tuple[List[Repository], List[Repository]]:
    library_repositories: List[Repository]
    plugin_repositories: List[Repository]
    if arg_library_repositories or arg_plugin_repositories:
        library_repositories = arg_library_repositories if arg_library_repositories is not None else []
        plugin_repositories = arg_plugin_repositories if arg_plugin_repositories is not None else []
        return library_repositories, plugin_repositories

    if conf_library_repositories or conf_plugin_repositories:
        library_repositories = conf_library_repositories if conf_library_repositories is not None else []
        plugin_repositories = conf_plugin_repositories if conf_plugin_repositories is not None else []
        return library_repositories, plugin_repositories

    message = ("No repositories provided! You can specify repositories to "
               "search artifact updates through configuration file.")
    raise KatalogerConfigurationException(message)


def find_cwd_catalogs() -> Optional[List[Catalog]]:
    catalog_files = Path.cwd().glob("*.versions.toml")
    catalog_paths = filter(file_exists, catalog_files)
    if not catalog_paths:
        return None

    return [Catalog.from_path(path) for path in catalog_paths]


def load_configuration_data(configuration_path: Optional[Path]) -> ConfigurationData:
    if not configuration_path:
        configuration_candidate = Path.cwd() / "default.configuration.toml"
        if file_exists(configuration_candidate):
            configuration_path = configuration_candidate
        else:
            configuration_path = get_package_file("default.configuration.toml")

    return load_configuration(configuration_path)
