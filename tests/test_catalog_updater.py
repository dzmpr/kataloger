from typing import List, Optional
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from entity_factory import EntityFactory
from kataloger.catalog_updater import CatalogUpdater
from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.update_resolver.base.update_resolution import UpdateResolution
from kataloger.update_resolver.base.update_resolver import UpdateResolver


class TestCatalogUpdater:

    def test_should_raise_configuration_exception_when_no_library_and_plugin_repositories_provided(self):
        with pytest.raises(KatalogerConfigurationException, match="No repositories provided!"):
            self._create_catalog_updater(
                library_repositories=[],
                plugin_repositories=[],
                update_resolvers=[Mock()],
            )

    def test_should_not_raise_configuration_exception_when_no_library_repositories_provided(self):
        repository: Repository = EntityFactory.create_repository()
        self._create_catalog_updater(
            library_repositories=[],
            plugin_repositories=[repository],
            update_resolvers=[Mock()],
        )

    def test_should_not_raise_configuration_exception_when_no_plugin_repositories_provided(self):
        repository: Repository = EntityFactory.create_repository()
        self._create_catalog_updater(
            library_repositories=[repository],
            plugin_repositories=[],
            update_resolvers=[Mock()],
        )

    def test_should_raise_configuration_exception_when_no_update_resolvers_provided(self):
        repository: Repository = EntityFactory.create_repository()
        with pytest.raises(KatalogerConfigurationException, match="No update resolvers provided!"):
            self._create_catalog_updater(
                library_repositories=[repository],
                plugin_repositories=[repository],
                update_resolvers=[],
            )

    def test_try_find_update_should_return_none_when_resolver_update_resolution_is_no_updates(self):
        library: Library = EntityFactory.create_library()
        repository: Repository = EntityFactory.create_repository()
        resolver_mock: Mock = self._create_resolver_mock(resolution=UpdateResolution.NO_UPDATES)

        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        actual_update: ArtifactUpdate = catalog_updater.try_find_update(artifact=library, repositories_metadata=[])

        assert actual_update is None
        resolver_mock.resolve.assert_called_once()

    def test_try_find_update_should_return_update_when_resolver_update_resolution_is_update_found(self):
        library: Library = EntityFactory.create_library()
        repository: Repository = EntityFactory.create_repository()
        expected_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=repository.name,
        )
        resolver_mock: Mock = self._create_resolver_mock(UpdateResolution.UPDATE_FOUND, expected_update)

        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        actual_update: ArtifactUpdate = catalog_updater.try_find_update(artifact=library, repositories_metadata=[])

        assert actual_update == expected_update
        resolver_mock.resolve.assert_called_once()

    def test_try_find_update_should_return_update_when_first_resolver_cant_resolve_update_but_second_does(self):
        library: Library = EntityFactory.create_library()
        repository: Repository = EntityFactory.create_repository()
        metadata_mock: List[Mock] = [Mock()]
        expected_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=repository.name,
        )
        first_resolver: Mock = self._create_resolver_mock(UpdateResolution.CANT_RESOLVE)
        second_resolver: Mock = self._create_resolver_mock(UpdateResolution.UPDATE_FOUND, expected_update)

        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            update_resolvers=[first_resolver, second_resolver],
        )
        actual_update: ArtifactUpdate = catalog_updater.try_find_update(
            artifact=library,
            repositories_metadata=metadata_mock,
        )

        assert actual_update == expected_update
        first_resolver.resolve.assert_called_once_with(library, metadata_mock)
        second_resolver.resolve.assert_called_once_with(library, metadata_mock)

    @pytest.mark.asyncio()
    async def test_get_library_updates_should_return_no_updates_when_there_is_no_library_repositories(self):
        library: Library = EntityFactory.create_library()
        repository: Repository = EntityFactory.create_repository()
        resolver_mock: Mock = self._create_resolver_mock(UpdateResolution.NO_UPDATES)
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            plugin_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        actual_updates: List[ArtifactUpdate] = await catalog_updater.get_library_updates(libraries=[library])

        assert actual_updates == []
        resolver_mock.resolve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_get_library_updates_should_get_metadata_for_libraries_and_return_not_none_updates(self):
        library: Library = EntityFactory.create_library()
        repository: Repository = EntityFactory.create_repository()
        expected_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=repository.name,
        )
        libraries = [library, library]
        resolver_mock: Mock = Mock()
        resolver_mock.resolve.side_effect = [
            (UpdateResolution.NO_UPDATES, None),
            (UpdateResolution.UPDATE_FOUND, expected_update),
        ]
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        repositories_metadata = {Mock(): Mock(), Mock(): Mock()}
        with patch(
            target="kataloger.catalog_updater.get_all_artifact_metadata",
            new=AsyncMock(return_value=repositories_metadata),
        ) as load_metadata_mock:
            actual_updates: List[ArtifactUpdate] = await catalog_updater.get_library_updates(libraries)

        assert actual_updates == [expected_update]
        assert resolver_mock.resolve.call_count == 2
        load_metadata_mock.assert_called_once_with(
            artifacts=libraries,
            repositories=[repository],
            verbose=False,
        )

    @pytest.mark.asyncio()
    async def test_get_plugin_updates_should_return_no_updates_when_there_is_no_plugin_repositories(self):
        plugin: Plugin = EntityFactory.create_plugin()
        repository: Repository = EntityFactory.create_repository()
        resolver_mock: Mock = self._create_resolver_mock(UpdateResolution.NO_UPDATES)
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        actual_updates: List[ArtifactUpdate] = await catalog_updater.get_plugin_updates(plugins=[plugin])

        assert actual_updates == []
        resolver_mock.resolve.assert_not_called()

    @pytest.mark.asyncio()
    async def test_get_plugin_updates_should_get_metadata_for_plugins_and_return_not_none_updates(self):
        plugin: Plugin = EntityFactory.create_plugin()
        repository: Repository = EntityFactory.create_repository()
        expected_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=plugin.name,
            update_repository_name=repository.name,
        )
        plugins = [plugin, plugin]
        resolver_mock: Mock = Mock()
        resolver_mock.resolve.side_effect = [
            (UpdateResolution.NO_UPDATES, None),
            (UpdateResolution.UPDATE_FOUND, expected_update),
        ]
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            plugin_repositories=[repository],
            update_resolvers=[resolver_mock],
        )
        repositories_metadata = {Mock(): Mock(), Mock(): Mock()}
        with patch(
            target="kataloger.catalog_updater.get_all_artifact_metadata",
            new=AsyncMock(return_value=repositories_metadata),
        ) as load_metadata_mock:
            actual_updates: List[ArtifactUpdate] = await catalog_updater.get_plugin_updates(plugins)

        assert actual_updates == [expected_update]
        assert resolver_mock.resolve.call_count == 2
        load_metadata_mock.assert_called_once_with(
            artifacts=plugins,
            repositories=[repository],
            verbose=False,
        )

    @pytest.mark.asyncio()
    async def test_get_updates_should_return_updates_for_libraries_and_plugins(self):
        library: Library = EntityFactory.create_library()
        plugin: Plugin = EntityFactory.create_plugin()
        library_repository: Repository = EntityFactory.create_repository(name="library_repository")
        plugin_repository: Repository = EntityFactory.create_repository(name="plugin_repository")
        library_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=library_repository.name,
        )
        plugin_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=plugin.name,
            update_repository_name=plugin_repository.name,
        )
        resolver_mock: Mock = Mock()
        resolver_mock.resolve.side_effect = [
            (UpdateResolution.UPDATE_FOUND, library_update),
            (UpdateResolution.UPDATE_FOUND, plugin_update),
        ]
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[library_repository],
            plugin_repositories=[plugin_repository],
            update_resolvers=[resolver_mock],
        )

        with patch(
            target="kataloger.catalog_updater.get_all_artifact_metadata",
            new=AsyncMock(return_value={Mock(): Mock()}),
        ) as load_metadata_mock:
            library_updates, plugin_updates = await catalog_updater.get_updates(libraries=[library], plugins=[plugin])

        assert library_updates == [library_update]
        assert plugin_updates == [plugin_update]
        assert resolver_mock.resolve.call_count == 2
        expected_load_metadata_calls = [
            call(
                artifacts=[library],
                repositories=[library_repository],
                verbose=False,
            ),
            call(
                artifacts=[plugin],
                repositories=[plugin_repository],
                verbose=False,
            ),
        ]
        assert load_metadata_mock.call_args_list == expected_load_metadata_calls

    @pytest.mark.asyncio()
    async def test_get_artifact_updates_should_return_artifact_updates_from_correct_repositories(self):
        library: Library = EntityFactory.create_library()
        plugin: Plugin = EntityFactory.create_plugin()
        library_repository: Repository = EntityFactory.create_repository(name="library_repository")
        plugin_repository: Repository = EntityFactory.create_repository(name="plugin_repository")
        library_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=library_repository.name,
        )
        plugin_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=plugin.name,
            update_repository_name=plugin_repository.name,
        )
        resolver_mock: Mock = Mock()
        resolver_mock.resolve.side_effect = [
            (UpdateResolution.UPDATE_FOUND, library_update),
            (UpdateResolution.UPDATE_FOUND, plugin_update),
        ]
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[library_repository],
            plugin_repositories=[plugin_repository],
            update_resolvers=[resolver_mock],
        )

        with patch(
            target="kataloger.catalog_updater.get_all_artifact_metadata",
            new=AsyncMock(return_value={Mock(): Mock()}),
        ) as load_metadata_mock:
            artifact_updates: List[ArtifactUpdate] = await catalog_updater.get_artifact_updates(
                artifacts=[library, plugin],
            )

        assert artifact_updates == [library_update, plugin_update]
        assert resolver_mock.resolve.call_count == 2
        expected_load_metadata_calls = [
            call(
                artifacts=[library],
                repositories=[library_repository],
                verbose=False,
            ),
            call(
                artifacts=[plugin],
                repositories=[plugin_repository],
                verbose=False,
            ),
        ]
        assert load_metadata_mock.call_args_list == expected_load_metadata_calls

    @pytest.mark.asyncio()
    async def test_should_return_empty_list_when_there_are_no_libraries_and_plugins_in_loaded_catalog(self):
        expected_updates: List[ArtifactUpdate] = []
        repository: Repository = EntityFactory.create_repository()
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[repository],
            plugin_repositories=[repository],
            update_resolvers=[Mock()],
        )
        with patch("kataloger.catalog_updater.load_catalog", Mock(return_value=([], []))):
            actual_updates: List[ArtifactUpdate] = await catalog_updater.get_catalog_updates(catalog_path=Mock())

        assert actual_updates == expected_updates

    @pytest.mark.asyncio()
    async def test_should_return_artifact_updates_when_there_are_libraries_and_plugins_in_loaded_catalog(self):
        library: Library = EntityFactory.create_library()
        plugin: Plugin = EntityFactory.create_plugin()
        library_repository: Repository = EntityFactory.create_repository(name="library_repository")
        plugin_repository: Repository = EntityFactory.create_repository(name="plugin_repository")
        library_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=library.name,
            update_repository_name=library_repository.name,
        )
        plugin_update: ArtifactUpdate = EntityFactory.create_artifact_update(
            name=plugin.name,
            update_repository_name=plugin_repository.name,
        )
        resolver_mock: Mock = Mock()
        resolver_mock.resolve.side_effect = [
            (UpdateResolution.UPDATE_FOUND, library_update),
            (UpdateResolution.UPDATE_FOUND, plugin_update),
        ]
        catalog_updater: CatalogUpdater = self._create_catalog_updater(
            library_repositories=[library_repository],
            plugin_repositories=[plugin_repository],
            update_resolvers=[resolver_mock],
        )

        load_metadata_mock = AsyncMock(return_value={Mock(): Mock()})
        with patch(target="kataloger.catalog_updater.load_catalog", new=Mock(return_value=([library], [plugin]))), \
             patch(target="kataloger.catalog_updater.get_all_artifact_metadata", new=load_metadata_mock):
            artifact_updates: List[ArtifactUpdate] = await catalog_updater.get_catalog_updates(catalog_path=Mock())

        assert artifact_updates == [library_update, plugin_update]
        assert resolver_mock.resolve.call_count == 2
        expected_load_metadata_calls = [
            call(
                artifacts=[library],
                repositories=[library_repository],
                verbose=False,
            ),
            call(
                artifacts=[plugin],
                repositories=[plugin_repository],
                verbose=False,
            ),
        ]
        assert load_metadata_mock.call_args_list == expected_load_metadata_calls

    @staticmethod
    def _create_resolver_mock(resolution: UpdateResolution, update: Optional[ArtifactUpdate] = None) -> Mock:
        resolver_mock = Mock()
        resolver_mock.resolve.return_value = (resolution, update)
        return resolver_mock

    @staticmethod
    def _create_catalog_updater(
        library_repositories: Optional[List[Repository]] = None,
        plugin_repositories: Optional[List[Repository]] = None,
        update_resolvers: Optional[List[UpdateResolver]] = None,
        verbose: bool = False,
    ) -> CatalogUpdater:
        if not library_repositories:
            library_repositories = []
        if not plugin_repositories:
            plugin_repositories = []
        if not update_resolvers:
            update_resolvers = []

        return CatalogUpdater(
            library_repositories=library_repositories,
            plugin_repositories=plugin_repositories,
            update_resolvers=update_resolvers,
            verbose=verbose,
        )
