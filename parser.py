import tomllib

from data.Library import Library
from data.Plugin import Plugin
from data.Repository import Repository


def load_repositories() -> tuple[list[Repository], list[Repository]]:
    library_repositories: list[Repository] = list()
    plugin_repositories: list[Repository] = list()
    repositories_data = load_toml_to_dict(path="./repositories.toml")
    if "libraries" in repositories_data:
        library_repositories = parse_repositories(repositories_data["libraries"].items())
    if "plugins" in repositories_data:
        plugin_repositories = parse_repositories(repositories_data["plugins"].items())
    if not len(library_repositories) and not len(plugin_repositories):
        raise Exception("No repositories provided!")
    return library_repositories, plugin_repositories


def load_catalog(catalog_path: str) -> tuple[list[Library], list[Plugin]]:
    catalog = load_toml_to_dict(catalog_path)

    if "versions" not in catalog or ("libraries" not in catalog and "plugins" not in catalog):
        raise Exception("Incorrect catalog format!")

    versions: dict = catalog.pop("versions")
    libraries = parse_libraries(catalog, versions)
    plugins = parse_plugins(catalog, versions)

    return libraries, plugins


def parse_repositories(repositories_data: list[tuple]) -> list[Repository]:
    repositories = list()
    for repository_data in repositories_data:
        match repository_data:
            case (str(name), str(address)):
                repository = Repository(name, address)
            case (str(name), dict(credentials)):
                if "address" not in credentials or "user" not in credentials or "password" not in credentials:
                    raise Exception(f"Credentials for \"{name}\" repository is incomplete!")
                repository = Repository(
                    name=name,
                    address=credentials["address"],
                    user=credentials["user"],
                    password=credentials["password"],
                )
            case _:
                raise ValueError("Unexpected repository data.")
        repositories.append(repository)
    return repositories


def parse_libraries(catalog: dict[str, str | dict], versions: dict) -> list[Library]:
    libraries = list()

    if "libraries" not in catalog:
        return libraries

    for name, library in catalog["libraries"].items():
        if "version" not in library:
            print(f"W: Library \"{library['module']}\" has no version in catalog.")
            continue
        libraries.append(Library(name=name, coordinates=library["module"], version=versions[library["version"]["ref"]]))
    return libraries


def parse_plugins(catalog: dict[str, str | dict], versions: dict) -> list[Plugin]:
    plugins = list()

    if "plugins" not in catalog:
        return plugins

    for name, plugin in catalog["plugins"].items():
        if "version" not in plugin:
            print(f"W: Plugin \"{plugin['id']}\" has no version in catalog.")
            continue
        plugins.append(Plugin(name=name, coordinates=plugin["id"], version=versions[plugin["version"]["ref"]]))
    return plugins


def load_toml_to_dict(path: str) -> dict[str, str | dict]:
    with open(path, 'rb') as file:
        return tomllib.load(file)
