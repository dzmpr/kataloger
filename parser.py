import tomllib

from data.Library import Library
from data.Plugin import Plugin


def load_catalog(path: str) -> dict[str, str | dict]:
    with open(path, 'rb') as version_catalog:
        return tomllib.load(version_catalog)


def parse(catalog_path: str) -> tuple[list[Library], list[Plugin]]:
    catalog = load_catalog(catalog_path)
    versions = catalog.pop("versions")

    libraries = list()
    for library in catalog["libraries"].values():
        if "version" not in library:
            print(f"W: Library \"{library['module']}\" has no version in catalog.")
            continue
        libraries.append(Library(name=library["module"], version=versions[library["version"]["ref"]]))

    plugins = list()
    for plugin in catalog["plugins"].values():
        if "version" not in plugin:
            print(f"W: Plugin \"{plugin['id']}\" has no version in catalog.")
            continue
        plugins.append(Plugin(group_id=plugin["id"], version=versions[plugin["version"]["ref"]]))
    return libraries, plugins
