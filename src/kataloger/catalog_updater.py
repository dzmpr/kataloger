from pathlib import Path
from typing import Optional

from kataloger.data.artifact.artifact import Artifact
from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.metadata_repository_info import MetadataRepositoryInfo
from kataloger.data.repository import Repository
from kataloger.execptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.helpers.log_helpers import log_warning
from kataloger.helpers.toml_parse_helpers import load_catalog
from kataloger.helpers.update_helpers import get_all_artifact_metadata
from kataloger.update_resolver.base.update_resolution import UpdateResolution
from kataloger.update_resolver.base.update_resolver import UpdateResolver


class CatalogUpdater:
    def __init__(
        self,
        library_repositories: list[Repository],
        plugin_repositories: list[Repository],
        update_resolvers: list[UpdateResolver],
        verbose: bool = False,
    ):
        if not (library_repositories or plugin_repositories):
            raise KatalogerConfigurationException("No repositories provided!")

        if not update_resolvers:
            raise KatalogerConfigurationException("No update resolvers provided!")

        self.library_repositories = library_repositories
        self.plugin_repositories = plugin_repositories
        self.update_resolvers = update_resolvers
        self.verbose = verbose

    async def get_catalog_updates(self, catalog_path: Path) -> list[ArtifactUpdate]:
        libraries, plugins = load_catalog(catalog_path, self.verbose)
        if not (libraries or plugins):
            if self.verbose:
                log_warning(f"Catalog \"{catalog_path.name}\" is empty.")
            return []

        library_updates, plugin_updates = await self.get_updates(libraries, plugins)
        return library_updates + plugin_updates

    async def get_artifact_updates(self, artifacts: list[Artifact]) -> list[ArtifactUpdate]:
        libraries = [artifact for artifact in artifacts if isinstance(artifact, Library)]
        plugins = [artifact for artifact in artifacts if isinstance(artifact, Plugin)]
        library_updates, plugin_updates = await self.get_updates(libraries, plugins)
        return library_updates + plugin_updates

    async def get_updates(
        self,
        libraries: list[Library],
        plugins: list[Plugin],
    ) -> tuple[list[ArtifactUpdate], list[ArtifactUpdate]]:
        library_updates = await self.get_library_updates(libraries)
        plugin_updates = await self.get_plugin_updates(plugins)
        return library_updates, plugin_updates

    async def get_library_updates(self, libraries: list[Library]) -> list[ArtifactUpdate]:
        library_updates: list[ArtifactUpdate] = []
        if not self.library_repositories:
            if self.verbose:
                log_warning("No repositories for libraries provided.")
            return library_updates

        library_update_info = await get_all_artifact_metadata(
            artifacts=libraries,
            repositories=self.library_repositories,
            verbose=self.verbose,
        )
        for (artifact, repositories_metadata) in library_update_info.items():
            library_updates.append(self.try_find_update(artifact, repositories_metadata))
        return list(filter(lambda item: item is not None, library_updates))

    async def get_plugin_updates(self, plugins: list[Plugin]) -> list[ArtifactUpdate]:
        plugin_updates: list[ArtifactUpdate] = []
        if not self.plugin_repositories:
            if self.verbose:
                log_warning("No repositories for plugins provided.")
            return plugin_updates

        plugin_update_info = await get_all_artifact_metadata(
            artifacts=plugins,
            repositories=self.plugin_repositories,
            verbose=self.verbose,
        )
        for (artifact, repositories_metadata) in plugin_update_info.items():
            plugin_updates.append(self.try_find_update(artifact, repositories_metadata))
        return list(filter(lambda item: item is not None, plugin_updates))

    def try_find_update(
        self,
        artifact: Artifact,
        repositories_metadata: list[MetadataRepositoryInfo],
    ) -> Optional[ArtifactUpdate]:
        for resolver in self.update_resolvers:
            (resolution, optional_update) = resolver.resolve(artifact, repositories_metadata)
            match resolution:
                case UpdateResolution.CANT_RESOLVE: continue
                case UpdateResolution.UPDATE_FOUND: return optional_update
                case UpdateResolution.NO_UPDATES: return None

        return None
