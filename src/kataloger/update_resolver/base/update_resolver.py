from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.update_resolver.base.update_resolution import UpdateResolution


class UpdateResolver(ABC):

    @abstractmethod
    def resolve(
        self,
        artifact: Artifact,
        repositories_metadata: List[MetadataRepositoryInfo],
    ) -> Tuple[UpdateResolution, Optional[ArtifactUpdate]]:
        raise NotImplementedError
