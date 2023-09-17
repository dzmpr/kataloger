from dataclasses import dataclass

from kataloger.data.artifact_metadata import ArtifactMetadata
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class MetadataRepositoryInfo:
    repository: Repository
    metadata: ArtifactMetadata
