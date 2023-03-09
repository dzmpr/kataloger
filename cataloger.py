import updater
from data.AvailableUpdate import AvailableUpdate
from parser import parse

gradle_plugin_portal_url = "https://plugins.gradle.org/m2"
google_repository_url = "https://dl.google.com/dl/android/maven2/"
maven_repository_url = "https://repo.maven.apache.org/maven2/"


def print_updates(updates: list[AvailableUpdate]):
    if len(updates) == 0:
        print("Your catalog is up to date!")
    else:
        artifact_with_max_len = max(updates, key=lambda x: len(x.artifact_id))
        max_artifact_id_len = len(artifact_with_max_len.artifact_id)
        print("Here is updates that I found:")
        for update in updates:
            dot_count = max_artifact_id_len - len(update.artifact_id) + 3
            print(f"{update.artifact_id} {'.' * dot_count} {update.current_version} => {update.available_version}")


if __name__ == '__main__':
    catalog_path = input("Input path to catalog .toml file: ")
    libraries, plugins = parse(catalog_path=catalog_path)
    repositories = [gradle_plugin_portal_url, google_repository_url, maven_repository_url]
    updates = updater.check_updates(repositories, libraries, plugins)
    print_updates(updates)
