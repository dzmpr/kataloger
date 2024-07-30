from typing import List

from kataloger.data.artifact_update import ArtifactUpdate


def print_catalog_updates(
    updates: List[ArtifactUpdate],
    catalog_name: str,
    catalog_count: int,
    verbose: bool,
) -> None:
    if catalog_count > 1:
        if updates:
            print(f'Updates for "{catalog_name}" catalog:')
        else:
            print(f'Catalog "{catalog_name}" is up to date!')

    for update in updates:
        version_part = f"{update.current_version} -> {update.available_version}"
        if verbose:
            print(f"[{update.update_repository_name}] {update.name} {version_part}")
        else:
            print(f"{update.name} {version_part}")

    if catalog_count > 1:
        print("")
