import tomllib
from pathlib import Path

from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.repository import Repository
from kataloger.execptions.kataloger_parse_exception import KatalogerParseException
from kataloger.helpers.log_helpers import log_warning


def load_repositories(repositories_path: Path) -> tuple[list[Repository], list[Repository]]:
    library_repositories: list[Repository] = []
    plugin_repositories: list[Repository] = []

    repositories_data = load_toml_to_dict(path=repositories_path)
    if "libraries" in repositories_data:
        library_repositories = parse_repositories(list(repositories_data["libraries"].items()))
    if "plugins" in repositories_data:
        plugin_repositories = parse_repositories(list(repositories_data["plugins"].items()))

    return library_repositories, plugin_repositories


def load_catalog(catalog_path: Path, verbose: bool) -> tuple[list[Library], list[Plugin]]:
    catalog = load_toml_to_dict(catalog_path)

    if "libraries" not in catalog and "plugins" not in catalog:
        raise KatalogerParseException(message="Catalog has no libraries and plugins to update.")

    # TODO: catalog can not contain versions section
    versions: dict[str, str] = catalog.pop("versions")
    libraries = parse_libraries(catalog, versions, verbose)
    plugins = parse_plugins(catalog, versions, verbose)

    return libraries, plugins


def parse_repositories(repositories_data: list[tuple]) -> list[Repository]:
    repositories = []
    for repository_data in repositories_data:
        match repository_data:
            case (str(name), str(address)):
                repository = Repository(name, address)
            case (str(name), dict(credentials)):
                if "address" not in credentials or "user" not in credentials or "password" not in credentials:
                    raise KatalogerParseException(message=f"Credentials for \"{name}\" repository is incomplete!")
                repository = Repository(
                    name=name,
                    address=credentials["address"],
                    user=credentials["user"],
                    password=credentials["password"],
                )
            case _:
                raise KatalogerParseException(message="Unexpected repository data.")
        repositories.append(repository)

    return repositories


def parse_libraries(catalog: dict[str, str | dict], versions: dict, verbose: bool) -> list[Library]:
    libraries = []

    if "libraries" not in catalog:
        return libraries

    for name, library in catalog["libraries"].items():
        if "version" not in library:
            if verbose:
                log_warning(f"Library \"{library['module']}\" has no version in catalog.")
            continue
        # TODO: Support not only 'version.ref', version can be inlined
        libraries.append(Library(name=name, coordinates=library["module"], version=versions[library["version"]["ref"]]))
    return libraries


def parse_plugins(catalog: dict[str, str | dict], versions: dict, verbose: bool) -> list[Plugin]:
    plugins = []
    if "plugins" not in catalog:
        return plugins

    for name, plugin in catalog["plugins"].items():
        if "version" not in plugin:
            if verbose:
                log_warning(f"Plugin \"{plugin['id']}\" has no version in catalog.")
            continue
        # TODO: Support not only 'version.ref', version can be inlined
        plugins.append(Plugin(name=name, coordinates=plugin["id"], version=versions[plugin["version"]["ref"]]))
    return plugins


def load_toml_to_dict(path: Path) -> dict[str, str | dict]:
    with open(path, 'rb') as file:
        return tomllib.load(file)
