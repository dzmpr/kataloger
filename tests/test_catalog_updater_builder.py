from unittest.mock import Mock, patch

import pytest

from entity_factory import EntityFactory
from kataloger import catalog_updater_builder
from kataloger.catalog_updater import CatalogUpdater
from kataloger.catalog_updater_builder import CatalogUpdaterBuilder
from kataloger.data.repository import Repository
from kataloger.execptions.kataloger_configuration_exception import KatalogerConfigurationException


class TestCatalogUpdaterBuilder:
    def test_set_repositories_should_not_fail_when_path_exists_and_its_a_file(self):
        path_mock: Mock = self._create_path_mock(exists=True, is_file=True)

        CatalogUpdaterBuilder().set_repositories_path(path_mock)

    def test_set_repositories_should_fail_when_path_exists_but_its_not_a_file(self):
        path_mock: Mock = self._create_path_mock(exists=True, is_file=False)

        with pytest.raises(KatalogerConfigurationException):
            CatalogUpdaterBuilder().set_repositories_path(path_mock)

    def test_set_repositories_should_fail_when_path_not_exists(self):
        path_mock: Mock = self._create_path_mock(exists=False, is_file=True)

        with pytest.raises(KatalogerConfigurationException):
            CatalogUpdaterBuilder().set_repositories_path(path_mock)

    def test_should_load_repositories_from_provided_path_and_create_catalog_updater_with_them(self):
        library_repository: Repository = EntityFactory.create_repository()
        plugin_repository: Repository = EntityFactory.create_repository()
        load_repositories_mock: Mock = Mock(return_value=([library_repository], [plugin_repository]))

        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            with patch.object(catalog_updater_builder, "load_repositories", load_repositories_mock):
                CatalogUpdaterBuilder().set_repositories_path(Mock()).build()

        init_mock.assert_called_once_with(
            library_repositories=[library_repository],
            plugin_repositories=[plugin_repository],
            update_resolvers=[],
            verbose=False,
        )

    def test_should_create_catalog_updater_with_added_library_repositories(self):
        library_repositories: list[Repository] = [EntityFactory.create_repository()]

        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            CatalogUpdaterBuilder().set_library_repositories(library_repositories).build()

        init_mock.assert_called_once_with(
            library_repositories=library_repositories,
            plugin_repositories=[],
            update_resolvers=[],
            verbose=False,
        )

    def test_should_create_catalog_updater_with_added_plugin_repositories(self):
        plugin_repositories: list[Repository] = [EntityFactory.create_repository()]

        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            CatalogUpdaterBuilder().set_plugin_repositories(plugin_repositories).build()

        init_mock.assert_called_once_with(
            library_repositories=[],
            plugin_repositories=plugin_repositories,
            update_resolvers=[],
            verbose=False,
        )

    def test_should_create_catalog_updater_with_added_update_resolvers(self):
        update_resolvers = [Mock()]

        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            CatalogUpdaterBuilder().set_resolvers(update_resolvers).build()

        init_mock.assert_called_once_with(
            library_repositories=[],
            plugin_repositories=[],
            update_resolvers=update_resolvers,
            verbose=False,
        )

    def test_should_create_catalog_updater_with_added_update_resolver(self):
        update_resolver = Mock()

        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            CatalogUpdaterBuilder().add_resolver(update_resolver).build()

        init_mock.assert_called_once_with(
            library_repositories=[],
            plugin_repositories=[],
            update_resolvers=[update_resolver],
            verbose=False,
        )

    def test_should_create_catalog_updater_in_verbose_mode_when_it_enabled(self):
        with patch.object(CatalogUpdater, "__init__", Mock(return_value=None)) as init_mock:
            CatalogUpdaterBuilder().set_verbose(verbose=True).build()

        init_mock.assert_called_once_with(
            library_repositories=[],
            plugin_repositories=[],
            update_resolvers=[],
            verbose=True,
        )

    @staticmethod
    def _create_path_mock(exists: bool, is_file: bool) -> Mock:
        path_mock: Mock = Mock()
        path_mock.exists.return_value = exists
        path_mock.is_file.return_value = is_file
        return path_mock
