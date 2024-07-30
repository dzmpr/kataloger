from typing import List, Optional, Tuple

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.update_resolver.base.update_resolution import UpdateResolution
from kataloger.update_resolver.base.update_resolver import UpdateResolver
from kataloger.update_resolver.universal.version import Version
from kataloger.update_resolver.universal.version_factory import VersionFactory


class UniversalUpdateResolver(UpdateResolver):

    def __init__(
        self,
        version_factories: List[VersionFactory[Version]],
        suggest_unstable_updates: bool,
    ):
        self.version_factories = version_factories
        self.suggest_unstable_updates = suggest_unstable_updates

    def resolve(
        self,
        artifact: Artifact,
        repositories_metadata: List[MetadataRepositoryInfo],
    ) -> Tuple[UpdateResolution, Optional[ArtifactUpdate]]:
        recently_updated_repository = self.__most_recently_updated_repository(repositories_metadata)
        current_version_repository = self.__repository_with_current_version(artifact.version, repositories_metadata)
        repositories_to_check: List[MetadataRepositoryInfo] = []
        if current_version_repository and recently_updated_repository != current_version_repository:
            repositories_to_check.append(current_version_repository)
        repositories_to_check.append(recently_updated_repository)

        for repository in repositories_to_check:
            for factory in self.version_factories:
                (resolution, optional_update) = self.__resolve_update_in_repository(artifact, factory, repository)
                if resolution == UpdateResolution.CANT_RESOLVE:
                    continue
                if resolution == UpdateResolution.NO_UPDATES or resolution == UpdateResolution.UPDATE_FOUND:
                    return resolution, optional_update

                message: str = f'Unexpected update resolution: "{resolution}".'
                raise ValueError(message)

        return UpdateResolution.CANT_RESOLVE, None

    def __resolve_update_in_repository(
        self,
        artifact: Artifact,
        version_factory: VersionFactory,
        repository_metadata: MetadataRepositoryInfo,
    ) -> Tuple[UpdateResolution, Optional[ArtifactUpdate]]:
        current_version = artifact.version
        if not version_factory.can_create(current_version):
            return UpdateResolution.CANT_RESOLVE, None

        artifact_version = version_factory.create(current_version)
        suggest_unstable = self.suggest_unstable_updates or artifact_version.is_pre_release()
        for version in reversed(repository_metadata.metadata.versions):
            if not version_factory.can_create(version):
                return UpdateResolution.CANT_RESOLVE, None

            update_version = version_factory.create(version)
            if update_version.is_pre_release() and not suggest_unstable:
                continue

            if artifact_version == update_version:
                return UpdateResolution.NO_UPDATES, None
            if artifact_version < update_version:
                update = ArtifactUpdate(
                    name=artifact.name,
                    update_repository_name=repository_metadata.repository.name,
                    current_version=current_version,
                    available_version=version,
                )
                return UpdateResolution.UPDATE_FOUND, update

        return UpdateResolution.CANT_RESOLVE, None

    @staticmethod
    def __most_recently_updated_repository(
        repositories_metadata: List[MetadataRepositoryInfo],
    ) -> MetadataRepositoryInfo:
        return max(repositories_metadata, key=lambda rm: rm.metadata.last_updated)

    @staticmethod
    def __repository_with_current_version(
        current_version: str,
        repositories_metadata: List[MetadataRepositoryInfo],
    ) -> Optional[MetadataRepositoryInfo]:
        for repository_metadata in repositories_metadata:
            if current_version in repository_metadata.metadata.versions:
                return repository_metadata
        return None
