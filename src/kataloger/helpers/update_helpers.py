from collections import defaultdict
from typing import Optional

import asyncio
from aiohttp import BasicAuth
from aiohttp import ClientSession

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.data.repository import Repository
from kataloger.helpers.log_helpers import log_warning
from kataloger.helpers.xml_parse_helpers import try_parse_maven_group_metadata


async def get_all_artifact_metadata(
    artifacts: list[Artifact],
    repositories: list[Repository],
    verbose: bool,
) -> dict[Artifact, list[MetadataRepositoryInfo]]:
    if not artifacts:
        return {}

    search_results: dict[Artifact, list[MetadataRepositoryInfo]] = defaultdict(lambda: [])
    for repository in repositories:
        result = await get_all_artifact_metadata_in_repository(repository, artifacts, verbose)
        for artifact, metadata in result.items():
            search_results[artifact].append(metadata)
    return search_results


async def get_all_artifact_metadata_in_repository(
    repository: Repository,
    artifacts: list[Artifact],
    verbose: bool,
) -> dict[Artifact, MetadataRepositoryInfo]:
    if repository.requires_authorization():
        auth = BasicAuth(login=repository.user, password=repository.password)
    else:
        auth = None

    async with ClientSession(auth=auth) as session:
        requests = []
        for artifact in artifacts:
            request = get_artifact_metadata(session, repository, artifact, verbose)
            requests.append(request)
        results = await asyncio.gather(*requests)

    artifact_to_metadata: dict[Artifact, MetadataRepositoryInfo] = {}
    for artifact, metadata in zip(artifacts, results):
        if metadata:
            artifact_to_metadata[artifact] = metadata
    return artifact_to_metadata


async def get_artifact_metadata(
    session: ClientSession,
    repository: Repository,
    artifact: Artifact,
    verbose: bool,
) -> Optional[MetadataRepositoryInfo]:
    metadata_url = repository.address / artifact.to_path() / "maven-metadata.xml"
    async with session.get(metadata_url) as response:
        if response.status != 200:
            return None

        metadata = try_parse_maven_group_metadata(await response.text())
        if not metadata and verbose:
            log_warning(f"Can't parse metadata for {artifact.name} in {repository.name}.")
        return MetadataRepositoryInfo(repository, metadata)
