import os.path

import parser
import updater
from data.ArtifactUpdateInfo import ArtifactUpdateInfo


def print_updates(updates: list[ArtifactUpdateInfo]):
    if len(updates) == 0:
        print("Your catalog is up to date!")
    else:
        artifact_with_longest_name = max(updates, key=lambda x: len(x.artifact_name))
        max_artifact_name_len = len(artifact_with_longest_name.artifact_name)
        print("Here are updates that I found:")
        for update in updates:
            dot_count = max_artifact_name_len - len(update.artifact_name) + 3
            print(f"{update.artifact_name} {'.' * dot_count} "
                  f"{update.current_version} => {update.update_candidates[0].latest_version} "
                  f"({update.update_candidates[0].repository.name})")


def is_catalog_path_valid(path: str):
    if not os.path.isfile(path):
        raise Exception("Catalog not found!")


if __name__ == '__main__':
    library_repositories, plugin_repositories = parser.load_repositories()
    catalog_path = input("Input path to catalog .toml file: ")
    is_catalog_path_valid(catalog_path)
    libraries, plugins = parser.load_catalog(catalog_path=catalog_path)
    library_updates = updater.check_updates(library_repositories, libraries)
    plugin_updates = updater.check_updates(plugin_repositories, plugins)
    print_updates(library_updates + plugin_updates)
