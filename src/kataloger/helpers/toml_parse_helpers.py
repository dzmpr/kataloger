import tomllib
from pathlib import Path

from yarl import URL

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
    versions: dict[str, str] = catalog.pop("versions", {})
    libraries = parse_libraries(catalog, versions, verbose)
    plugins = parse_plugins(catalog, versions, verbose)

    return libraries, plugins


def parse_repositories(repositories_data: list[tuple]) -> list[Repository]:
    repositories = []
    for repository_data in repositories_data:
        match repository_data:
            case (str(name), str(address)):
                repository = Repository(name, URL(address))
            case (str(name), {"address": str(address), "user": str(user), "password": str(password)}):
                repository = Repository(
                    name=name,
                    address=URL(address),
                    user=user,
                    password=password,
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
        match library:
            case {"module": str(module), "version": str(version)}:
                library = Library(
                    name=name,
                    coordinates=module,
                    version=version,
                )
                libraries.append(library)
            case {"module": str(module), "version": {"ref": str(ref)}}:
                if not (version := versions.get(ref)):
                    raise KatalogerParseException(f"Version for \"{name}\" not specified by reference \"{ref}\".")

                library = Library(
                    name=name,
                    coordinates=module,
                    version=version,
                )
                libraries.append(library)
            case {"module": str(module)}:
                if verbose:
                    log_warning(f"Library \"{module}\" has no version in catalog.")
            case _:
                raise KatalogerParseException(f"Unknown library notation: {library}")

    return libraries


def parse_plugins(catalog: dict[str, str | dict], versions: dict, verbose: bool) -> list[Plugin]:
    plugins = []
    if "plugins" not in catalog:
        return plugins

    for name, plugin in catalog["plugins"].items():
        match plugin:
            case {"id": str(plugin_id), "version": str(version)}:
                plugin = Plugin(
                    name=name,
                    coordinates=plugin_id,
                    version=version,
                )
                plugins.append(plugin)
            case {"id": str(plugin_id), "version": {"ref": str(ref)}}:
                if not (version := versions.get(ref)):
                    raise KatalogerParseException(f"There is no version for \"{name}\" by key \"{ref}\".")

                plugin = Plugin(
                    name=name,
                    coordinates=plugin_id,
                    version=version,
                )
                plugins.append(plugin)
            case {"id": str(plugin_id)}:
                if verbose:
                    log_warning(f"Plugin \"{plugin_id}\" has no version in catalog.")
            case _:
                raise KatalogerParseException(f"Unknown plugin notation: {plugin}")

    return plugins


def load_toml_to_dict(path: Path) -> dict[str, str | dict]:
    with open(path, 'rb') as file:
        try:
            return tomllib.load(file)
        except tomllib.TOMLDecodeError:
            raise KatalogerParseException(f"Can't parse TOML in \"{path.name}\".")
