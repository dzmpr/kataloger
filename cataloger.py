import parser
import updater
from data.AvailableUpdate import AvailableUpdate


def print_updates(updates: list[AvailableUpdate]):
    if len(updates) == 0:
        print("Your catalog is up to date!")
    else:
        artifact_with_longest_name = max(updates, key=lambda x: len(x.artifact_name))
        max_artifact_name_len = len(artifact_with_longest_name.artifact_name)
        print("Here are updates that I found:")
        for update in updates:
            dot_count = max_artifact_name_len - len(update.artifact_name) + 3
            print(f"{update.artifact_name} {'.' * dot_count} " +
                  f"{update.current_version} => {update.available_version} ({update.repository_name})")


if __name__ == '__main__':
    repositories = parser.load_repositories()
    catalog_path = input("Input path to catalog .toml file: ")
    libraries, plugins = parser.load_catalog(catalog_path=catalog_path)
    artifact_updates = updater.check_updates(repositories, libraries, plugins)
    print_updates(artifact_updates)
