import asyncio
from collections import defaultdict
from typing import Dict, List, Optional

from aiohttp import BasicAuth, ClientSession

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.data.repository import Repository
from kataloger.helpers.log_helpers import log_warning
from kataloger.helpers.xml_parse_helpers import try_parse_maven_group_metadata


async def get_all_artifact_metadata(
    artifacts: List[Artifact],
    repositories: List[Repository],
    verbose: bool,
) -> Dict[Artifact, List[MetadataRepositoryInfo]]:
    if not artifacts:
        return {}

    search_results: Dict[Artifact, List[MetadataRepositoryInfo]] = defaultdict(list)
    for repository in repositories:
        result = await get_all_artifact_metadata_in_repository(repository, artifacts, verbose)
        for artifact, metadata in result.items():
            search_results[artifact].append(metadata)
    return search_results


async def get_all_artifact_metadata_in_repository(
    repository: Repository,
    artifacts: List[Artifact],
    verbose: bool,
) -> Dict[Artifact, MetadataRepositoryInfo]:
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

    return {artifact: metadata for artifact, metadata in zip(artifacts, results) if metadata}


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
