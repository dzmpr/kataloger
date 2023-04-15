from concurrent.futures import ThreadPoolExecutor, as_completed

import requests as requests
import xmltodict as xmltodict

from data.Artifact import Artifact
from data.ArtifactMetadata import ArtifactMetadata
from data.ArtifactUpdateInfo import ArtifactUpdateInfo
from data.Repository import Repository


def check_updates(
    repositories: list[Repository],
    artifacts: list[Artifact],
) -> list[ArtifactUpdateInfo]:
    if not repositories or not artifacts:
        return list()

    available_updates = list()
    with ThreadPoolExecutor(max_workers=80) as executor:
        futures = [executor.submit(handle_artifact, artifact, repositories) for artifact in artifacts]

        for future in as_completed(futures):
            if (result := future.result()) is not None:
                available_updates.append(result)
    return available_updates


def handle_artifact(artifact: Artifact, repositories: list[Repository]) -> ArtifactUpdateInfo | None:
    artifact_path = artifact.to_path()
    update_candidates = list()
    for repository in repositories:
        version_data = load_artifact_metadata(repository, artifact_path)
        if version_data is not None:
            update_candidates.append(version_data)

    if not update_candidates:
        return None
    else:
        return ArtifactUpdateInfo(artifact.name, artifact.version, update_candidates)


def load_artifact_metadata(repository: Repository, artifact_path: str) -> ArtifactMetadata | None:
    if repository.requires_authorization():
        auth = (repository.user, repository.password)
    else:
        auth = None

    metadata_url = f"{repository.address}{artifact_path}/maven-metadata.xml"
    response = requests.get(url=metadata_url, auth=auth)

    if response.status_code != 200:
        return None
    else:
        version_data = xmltodict.parse(response.text)["metadata"]["versioning"]
        return ArtifactMetadata(
            repository=repository,
            latest_version=version_data["latest"],
            release_version=version_data["release"],
            versions=version_data["versions"]["version"],
        )
