import requests as requests
import xmltodict as xmltodict

from data.ArtifactMetadata import ArtifactMetadata
from data.AvailableUpdate import AvailableUpdate
from data.Library import Library
from data.Plugin import Plugin


def check_updates(
        repositories: list[str],
        libraries: list[Library],
        plugins: list[Plugin],
) -> list[AvailableUpdate]:
    available_updates = list()
    for library in libraries:
        if (update := try_get_update(library.name, library.version, repositories)) is not None:
            available_updates.append(update)
    return available_updates


def try_get_update(artifact_ga: str, current_version: str, repositories: list[str]) -> AvailableUpdate | None:
    for repository in repositories:
        version_data = load_artifact_metadata(repository, artifact_ga)
        if version_data is not None:
            if version_data.latest_version != current_version:
                return AvailableUpdate(artifact_ga, current_version, version_data.latest_version)
            else:
                return None
    return None


def load_artifact_metadata(repository_url: str, artifact_name: str) -> ArtifactMetadata | None:
    artifact_path = artifact_name.replace(".", "/").replace(":", "/")
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
