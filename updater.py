from concurrent.futures import ThreadPoolExecutor, as_completed

import requests as requests
import xmltodict as xmltodict

from data.Artifact import Artifact
from data.ArtifactMetadata import ArtifactMetadata
from data.AvailableUpdate import AvailableUpdate
from data.Library import Library
from data.Plugin import Plugin
from data.Repository import Repository


def check_updates(
    repositories: tuple[list[Repository], list[Repository]],
    libraries: list[Library],
    plugins: list[Plugin],
) -> list[AvailableUpdate]:
    library_repositories, plugin_repositories = repositories
    available_updates = list()
    with ThreadPoolExecutor(max_workers=80) as executor:
        futures = list()
        for library in libraries:
            future = executor.submit(handle_artifact, library, library_repositories)
            futures.append(future)
        for plugin in plugins:
            future = executor.submit(handle_artifact, plugin, plugin_repositories)
            futures.append(future)

        for future in as_completed(futures):
            if (result := future.result()) is not None:
                available_updates.append(result)
    return available_updates


def handle_artifact(artifact: Artifact, repositories: list[Repository]) -> AvailableUpdate | None:
    artifact_path = artifact.to_path()
    for repository in repositories:
        version_data = load_artifact_metadata(repository.address, artifact_path)
        if version_data is not None:
            if version_data.latest_version != artifact.version:
                return AvailableUpdate(artifact.name, repository.name, artifact.version, version_data.latest_version)
            else:
                return None
    return None


def load_artifact_metadata(repository_url: str, artifact_path: str) -> ArtifactMetadata | None:
    metadata_url = f"{repository_url}{artifact_path}/maven-metadata.xml"
    response = requests.get(url=metadata_url)
    if response.status_code != 200:
        return None
    else:
        version_data = xmltodict.parse(response.text)["metadata"]["versioning"]
        return ArtifactMetadata(
            latest_version=version_data["latest"],
            release_version=version_data["release"],
            versions=version_data["versions"]["version"],
        )
