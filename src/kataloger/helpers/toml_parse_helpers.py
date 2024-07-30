from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from yarl import URL

from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException
from kataloger.helpers.backport_helpers import load_toml
from kataloger.helpers.log_helpers import log_warning
from kataloger.helpers.path_helpers import str_to_path
from kataloger.helpers.structural_matching_helpers import match


def load_configuration(configuration_path: Path) -> ConfigurationData:
    catalogs: Optional[List[Catalog]] = None
    library_repositories: Optional[List[Repository]] = None
    plugin_repositories: Optional[List[Repository]] = None

    configuration_data = load_toml(path=configuration_path)
    if "catalogs" in configuration_data:
        catalogs = parse_catalogs(configuration_data["catalogs"], configuration_root_dir=configuration_path.parent)
    if "libraries" in configuration_data:
        library_repositories = parse_repositories(configuration_data["libraries"])
    if "plugins" in configuration_data:
        plugin_repositories = parse_repositories(configuration_data["plugins"])

    return ConfigurationData(
        catalogs=catalogs,
        library_repositories=library_repositories,
        plugin_repositories=plugin_repositories,
        verbose=__extract_optional_boolean(configuration_data, key="verbose"),
        suggest_unstable_updates=__extract_optional_boolean(configuration_data, key="suggest_unstable_updates"),
        fail_on_updates=__extract_optional_boolean(configuration_data, key="fail_on_updates"),
    )


def load_catalog(catalog_path: Path, verbose: bool) -> Tuple[List[Library], List[Plugin]]:
    catalog = load_toml(catalog_path)
    versions: Dict[str, str] = catalog.pop("versions", {})
    libraries = parse_libraries(catalog, versions, verbose)
    plugins = parse_plugins(catalog, versions, verbose)

    return libraries, plugins


def parse_repositories(data: Dict) -> Optional[List[Repository]]:
    if not data:
        return None

    if not isinstance(data, dict):
        raise KatalogerParseException(message="Unexpected repository data.")

    repositories = []
    for name, repository_data in data.items():
        if not isinstance(name, str):
            raise KatalogerParseException(message=f'Unexpected repository name: "{name}".')

        repository: Repository
        if isinstance(repository_data, str):
            repository = Repository(name=name, address=URL(repository_data))
        elif mr := match(repository_data, pattern={"address": str, "user": str, "password": str}):
            repository = Repository(
                name=name,
                address=URL(mr.address),
                user=mr.user,
                password=mr.password,
            )
        else:
            raise KatalogerParseException(message="Unexpected repository data.")
        repositories.append(repository)

    return repositories


def parse_catalogs(data: Union[List, Dict], configuration_root_dir: Optional[Path]) -> Optional[List[Catalog]]:
    if not data:
        return None

    catalogs = []
    if isinstance(data, list):
        for path in data:
            if not isinstance(path, str):
                raise KatalogerParseException(message=f'Unexpected catalog path: "{path}".')
            if not path.strip():
                raise KatalogerParseException(message="Catalog path can't be empty!")

            catalogs.append(Catalog.from_path(path=str_to_path(path, root_path=configuration_root_dir)))
        return catalogs

    if isinstance(data, dict):
        for name, path in data.items():
            if not isinstance(name, str):
                raise KatalogerParseException(message=f'Unexpected catalog name: "{name}".')
            if not isinstance(path, str):
                raise KatalogerParseException(message=f'Unexpected catalog path: "{path}".')
            if not name.strip():
                raise KatalogerParseException(message="Catalog name can't be empty!")
            if not path.strip():
                raise KatalogerParseException(message=f'Catalog "{name}" has empty path!')

            catalogs.append(Catalog(name=name, path=str_to_path(path, root_path=configuration_root_dir)))
        return catalogs

    raise KatalogerParseException(message=f'Unexpected catalogs data format: "{data}".')


def parse_libraries(catalog: Dict[str, Union[Dict, str]], versions: Dict, verbose: bool) -> List[Library]:
    libraries = []
    if "libraries" not in catalog:
        return libraries

    for name, library_data in catalog["libraries"].items():
        if not isinstance(name, str):
            raise KatalogerParseException(message=f'Unexpected library name: "{name}".')

        library: Library
        if isinstance(library_data, str):
            (module, version) = __parse_declaration(library_data)
            library = Library(name=name, coordinates=module, version=version)
        elif mr := match(library_data, pattern={"group": str, "name": str, "version": str}):
            library = Library(
                name=name,
                coordinates=f"{mr.group}:{mr.name}",
                version=mr.version,
            )
        elif mr := match(library_data, pattern={"group": str, "name": str, "version": {"ref": str}}):
            library = Library(
                name=name,
                coordinates=f"{mr.group}:{mr.name}",
                version=__get_version_by_reference(versions, mr.version.ref, name),
            )
        elif mr := match(library_data, pattern={"module": str, "version": str}):
            library = Library(
                name=name,
                coordinates=mr.module,
                version=mr.version,
            )
        elif mr := match(library_data, pattern={"module": str, "version": {"ref": str}}):
            library = Library(
                name=name,
                coordinates=mr.module,
                version=__get_version_by_reference(versions, mr.version.ref, name),
            )
        elif mr := match(library_data, pattern={"module": str}):
            if verbose:
                log_warning(f'Library "{mr.module}" has no version in catalog.')
            continue
        else:
            message = f"Unknown library notation: {library_data}"
            raise KatalogerParseException(message)

        libraries.append(library)

    return libraries


def parse_plugins(catalog: Dict[str, Union[Dict, str]], versions: Dict, verbose: bool) -> List[Plugin]:
    plugins = []
    if "plugins" not in catalog:
        return plugins

    for name, plugin_data in catalog["plugins"].items():
        if not isinstance(name, str):
            raise KatalogerParseException(message=f'Unexpected plugin name: "{name}".')

        if isinstance(plugin_data, str):
            (plugin_id, version) = __parse_declaration(plugin_data)
            plugin = Plugin(name=name, coordinates=plugin_id, version=version)
        elif mr := match(plugin_data, pattern={"id": str, "version": str}):
            plugin = Plugin(
                name=name,
                coordinates=mr.id,
                version=mr.version,
            )
        elif mr := match(plugin_data, pattern={"id": str, "version": {"ref": str}}):
            plugin = Plugin(
                name=name,
                coordinates=mr.id,
                version=__get_version_by_reference(versions, mr.version.ref, name),
            )
        elif mr := match(plugin_data, pattern={"id": str}):
            if verbose:
                log_warning(f'Plugin "{mr.id}" has no version in catalog.')
            continue
        else:
            message = f"Unknown plugin notation: {plugin_data}"
            raise KatalogerParseException(message)

        plugins.append(plugin)

    return plugins


def __parse_declaration(declaration: str) -> Tuple[str, str]:
    components = declaration.rsplit(":", 1)
    if len(components) != 2 or not (components[0].strip() and components[1].strip()):
        message = f'Unknown declaration format: "{declaration}".'
        raise KatalogerParseException(message)
    return components[0], components[1]


def __get_version_by_reference(
    versions: Dict[str, str],
    version_ref: str,
    artifact_name: str,
) -> str:
    if not (version := versions.get(version_ref)):
        message = f'Version for "{artifact_name}" not specified by reference "{version_ref}".'
        raise KatalogerParseException(message)

    return version


def __extract_optional_boolean(data: Dict, key: str) -> Optional[bool]:
    value = data.get(key)
    if value is None or isinstance(value, bool):
        return value

    message = f'Configuration field "{key}" has incorrect value "{value}", while expected boolean type.'
    raise KatalogerParseException(message)
