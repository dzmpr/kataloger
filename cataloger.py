import os.path
from argparse import ArgumentParser

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


def get_arguments_input():
    arg_parser = ArgumentParser(
        prog="cataloger",
        description="Script which helps to find artifact updates.",
    )
    arg_parser.add_argument(
        "-p", "--path",
        type=str,
        dest="catalog_path",
        metavar="path",
        required=True,
        help="Path to gradle versions catalog.",
    )
    arg_parser.add_argument(
        "-rp", "--repositories-path",
        type=str,
        dest="repositories_path",
        metavar="path",
        help="Path to .toml file with repositories credentials.",
    )
    arguments = arg_parser.parse_args()

    if not arguments.repositories_path:
        repositories_path = "./repositories.toml"
    else:
        repositories_path = arguments.repositories_path

    is_file_exists(arguments.catalog_path)
    is_file_exists(repositories_path)
    return arguments.catalog_path, repositories_path


def is_file_exists(path: str):
    if not os.path.isfile(path):
        raise Exception(f"File not exists by path: \"{path}\"")


if __name__ == '__main__':
    catalog_path, repositories_path = get_arguments_input()

    library_repositories, plugin_repositories = parser.load_repositories(repositories_path=repositories_path)

    libraries, plugins = parser.load_catalog(catalog_path=catalog_path)
    library_updates = updater.check_updates(library_repositories, libraries)
    plugin_updates = updater.check_updates(plugin_repositories, plugins)
    print_updates(library_updates + plugin_updates)
