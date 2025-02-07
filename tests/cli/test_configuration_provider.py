from pathlib import Path
from typing import List, Optional
from unittest.mock import Mock

import pytest
from yarl import URL

from kataloger.cli import configuration_provider
from kataloger.cli.configuration_provider import get_catalogs, get_configuration, get_repositories
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.kataloger_arguments import KatalogerArguments
from kataloger.data.kataloger_configuration import KatalogerConfiguration
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_configuration_exception import KatalogerConfigurationException


class TestConfigurationProvider:

    default_arg_catalogs: List[Catalog] = [Catalog(name="arg_catalog", path=Path())]
    default_conf_catalogs: List[Catalog] = [Catalog(name="conf_catalog", path=Path())]
    default_cwd_catalogs: List[Catalog] = [Catalog(name="cwd_catalog", path=Path())]
    default_arg_library_repositories: List[Repository] = [Repository(name="arg_library_repository", address=URL())]
    default_arg_plugin_repositories: List[Repository] = [Repository(name="arg_plugin_repository", address=URL())]
    default_conf_library_repositories: List[Repository] = [Repository(name="conf_library_repository", address=URL())]
    default_conf_plugin_repositories: List[Repository] = [Repository(name="conf_plugin_repository", address=URL())]

    def test_should_return_arg_catalogs_when_arg_catalogs_is_not_none_or_empty(self):
        self.__test_get_catalogs(
            arg_catalogs=self.default_arg_catalogs,
            conf_catalogs=self.default_conf_catalogs,
            cwd_catalogs=self.default_cwd_catalogs,
            expected_catalogs=self.default_arg_catalogs,
        )

    def test_should_return_conf_catalogs_when_arg_catalogs_are_none(self):
        self.__test_get_catalogs(
            arg_catalogs=None,
            conf_catalogs=self.default_conf_catalogs,
            cwd_catalogs=self.default_cwd_catalogs,
            expected_catalogs=self.default_conf_catalogs,
        )

    def test_should_return_conf_catalogs_when_there_are_no_arg_catalogs(self):
        self.__test_get_catalogs(
            arg_catalogs=[],
            conf_catalogs=self.default_conf_catalogs,
            cwd_catalogs=self.default_cwd_catalogs,
            expected_catalogs=self.default_conf_catalogs,
        )

    def test_should_return_cwd_catalogs_when_conf_catalogs_are_none(self):
        self.__test_get_catalogs(
            arg_catalogs=None,
            conf_catalogs=None,
            cwd_catalogs=self.default_cwd_catalogs,
            expected_catalogs=self.default_cwd_catalogs,
        )

    def test_should_return_cwd_catalogs_when_there_are_no_conf_catalogs(self):
        self.__test_get_catalogs(
            arg_catalogs=None,
            conf_catalogs=[],
            cwd_catalogs=self.default_cwd_catalogs,
            expected_catalogs=self.default_cwd_catalogs,
        )

    def test_should_raise_exception_when_cwd_catalogs_are_none(self):
        configuration_provider.find_cwd_catalogs = Mock(return_value=None)

        with pytest.raises(KatalogerConfigurationException):
            get_catalogs(arg_catalogs=None, conf_catalogs=None)

    def test_should_raise_exception_when_there_are_no_cwd_catalogs(self):
        configuration_provider.find_cwd_catalogs = Mock(return_value=[])

        with pytest.raises(KatalogerConfigurationException):
            get_catalogs(arg_catalogs=None, conf_catalogs=None)

    def test_should_return_arg_repositories_when_there_are_arg_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=self.default_arg_library_repositories,
            arg_plugin_repositories=self.default_arg_plugin_repositories,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=self.default_arg_library_repositories,
            expected_plugin_repositories=self.default_arg_plugin_repositories,
        )

    def test_should_return_arg_repositories_when_there_are_plugin_repositories_but_library_repositories_are_none(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=self.default_arg_plugin_repositories,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=[],
            expected_plugin_repositories=self.default_arg_plugin_repositories,
        )

    def test_should_return_arg_repositories_when_there_are_plugin_repositories_but_no_library_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=[],
            arg_plugin_repositories=self.default_arg_plugin_repositories,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=[],
            expected_plugin_repositories=self.default_arg_plugin_repositories,
        )

    def test_should_return_arg_repositories_when_there_are_library_repositories_but_plugin_repositories_are_none(self):
        self.__test_get_repositories(
            arg_library_repositories=self.default_arg_library_repositories,
            arg_plugin_repositories=None,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=self.default_arg_library_repositories,
            expected_plugin_repositories=[],
        )

    def test_should_return_arg_repositories_when_there_are_library_repositories_but_no_plugin_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=self.default_arg_library_repositories,
            arg_plugin_repositories=[],
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=self.default_arg_library_repositories,
            expected_plugin_repositories=[],
        )

    def test_should_return_conf_repositories_when_there_are_no_arg_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=None,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=self.default_conf_library_repositories,
            expected_plugin_repositories=self.default_conf_plugin_repositories,
        )

    def test_should_return_conf_repositories_when_there_are_library_repositories_but_no_plugin_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=None,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=[],
            expected_library_repositories=self.default_conf_library_repositories,
            expected_plugin_repositories=[],
        )

    def test_should_return_conf_repositories_when_there_are_library_repositories_but_plugin_repositories_are_none(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=None,
            conf_library_repositories=self.default_conf_library_repositories,
            conf_plugin_repositories=None,
            expected_library_repositories=self.default_conf_library_repositories,
            expected_plugin_repositories=[],
        )

    def test_should_return_conf_repositories_when_there_are_plugin_repositories_but_no_library_repositories(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=None,
            conf_library_repositories=[],
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=[],
            expected_plugin_repositories=self.default_conf_plugin_repositories,
        )

    def test_should_return_conf_repositories_when_there_are_plugin_repositories_but_library_repositories_are_none(self):
        self.__test_get_repositories(
            arg_library_repositories=None,
            arg_plugin_repositories=None,
            conf_library_repositories=None,
            conf_plugin_repositories=self.default_conf_plugin_repositories,
            expected_library_repositories=[],
            expected_plugin_repositories=self.default_conf_plugin_repositories,
        )

    def test_should_raise_exception_when_there_are_no_arg_or_conf_repositories(self):
        with pytest.raises(KatalogerConfigurationException):
            get_repositories(
                arg_library_repositories=None,
                arg_plugin_repositories=None,
                conf_library_repositories=None,
                conf_plugin_repositories=None,
            )

    def test_should_return_args_configuration_flags_when_args_configuration_data_has_values(self):
        self.__test_get_configuration(
            args_fields_value=True,
            conf_fields_value=False,
            expected_value=True,
        )

    def test_should_return_conf_configuration_flags_when_args_configuration_data_values_is_none(self):
        self.__test_get_configuration(
            args_fields_value=None,
            conf_fields_value=True,
            expected_value=True,
        )

    def test_should_return_default_configuration_flags_when_args_and_conf_configuration_data_values_is_none(self):
        self.__test_get_configuration(
            args_fields_value=None,
            conf_fields_value=None,
            expected_value=False,
        )

    def __test_get_configuration(
        self,
        args_fields_value: Optional[bool],
        conf_fields_value: Optional[bool],
        expected_value: bool,
    ) -> None:
        args_configuration_data: ConfigurationData = ConfigurationData(
            catalogs=self.default_arg_catalogs,
            library_repositories=self.default_arg_library_repositories,
            plugin_repositories=self.default_arg_plugin_repositories,
            verbose=args_fields_value,
            suggest_unstable_updates=args_fields_value,
            fail_on_updates=args_fields_value,
        )
        arguments: KatalogerArguments = KatalogerArguments(
            configuration_path=None,
            configuration_data=args_configuration_data,
        )
        configuration_provider.parse_arguments = Mock(return_value=arguments)
        conf_configuration_data: ConfigurationData = ConfigurationData(
            catalogs=None,
            library_repositories=None,
            plugin_repositories=None,
            verbose=conf_fields_value,
            suggest_unstable_updates=conf_fields_value,
            fail_on_updates=conf_fields_value,
        )
        configuration_provider.load_configuration_data = Mock(return_value=conf_configuration_data)

        expected_configuration: KatalogerConfiguration = KatalogerConfiguration(
            catalogs=self.default_arg_catalogs,
            library_repositories=self.default_arg_library_repositories,
            plugin_repositories=self.default_arg_plugin_repositories,
            verbose=expected_value,
            suggest_unstable_updates=expected_value,
            fail_on_updates=expected_value,
        )
        actual_configuration: KatalogerConfiguration = get_configuration()

        assert actual_configuration == expected_configuration

    @staticmethod
    def __test_get_repositories(
        arg_library_repositories: Optional[List[Repository]],
        arg_plugin_repositories: Optional[List[Repository]],
        conf_library_repositories: Optional[List[Repository]],
        conf_plugin_repositories: Optional[List[Repository]],
        expected_library_repositories: List[Repository],
        expected_plugin_repositories: List[Repository],
    ):
        actual_library_repositories: List[Repository]
        actual_plugin_repositories: List[Repository]
        actual_library_repositories, actual_plugin_repositories = get_repositories(
            arg_library_repositories=arg_library_repositories,
            arg_plugin_repositories=arg_plugin_repositories,
            conf_library_repositories=conf_library_repositories,
            conf_plugin_repositories=conf_plugin_repositories,
        )

        assert actual_library_repositories == expected_library_repositories
        assert actual_plugin_repositories == expected_plugin_repositories

    @staticmethod
    def __test_get_catalogs(
        arg_catalogs: Optional[List[Catalog]],
        conf_catalogs: Optional[List[Catalog]],
        cwd_catalogs: Optional[List[Catalog]],
        expected_catalogs: List[Catalog],
    ):
        configuration_provider.find_cwd_catalogs = Mock(return_value=cwd_catalogs)
        actual_catalogs: List[Catalog] = get_catalogs(arg_catalogs, conf_catalogs)

        assert actual_catalogs == expected_catalogs
