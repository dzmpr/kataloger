from abc import abstractmethod, ABC
from typing import Optional

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.update_resolver.base.update_resolution import UpdateResolution


class UpdateResolver(ABC):

    @abstractmethod
    def resolve(
        self,
        artifact: Artifact,
        repositories_metadata: list[MetadataRepositoryInfo],
    ) -> tuple[UpdateResolution, Optional[ArtifactUpdate]]:
        raise NotImplementedError
