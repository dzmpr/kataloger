from pathlib import Path
from typing import Dict, List, Optional, Tuple
from unittest.mock import Mock

import pytest
from yarl import URL

from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.catalog import Catalog
from kataloger.data.configuration_data import ConfigurationData
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException
from kataloger.helpers import toml_parse_helpers
from kataloger.helpers.toml_parse_helpers import (
    load_catalog,
    load_configuration,
    parse_catalogs,
    parse_libraries,
    parse_plugins,
    parse_repositories,
)


class TestTomlParseHelpers:
    default_artifact_name: str = "artifact_name"
    default_plugin_id: str = "com.plug.in"
    default_library_module: str = "com.library:library-core"
    default_version: str = "1.0.0"
    default_repository_name: str = "repository_name"
    default_repository_address: str = "https://reposito.ry/"
    default_catalog_name: str = "catalog_name"

    def test_should_return_empty_plugins_list_when_catalog_has_no_plugins(self):
        catalog: Dict = {"libraries": {}}
        expected_plugins: List[Plugin] = []
        actual_plugins: List[Plugin] = parse_plugins(catalog, versions={}, verbose=False)

        assert actual_plugins == expected_plugins

    def test_should_parse_plugin_when_it_has_declaration(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: f"{self.default_plugin_id}:{self.default_version}",
            },
        }
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )
        actual_plugins: List[Plugin] = parse_plugins(catalog, versions={}, verbose=False)

        assert actual_plugins == [expected_plugin]

    def test_should_raise_exception_when_plugin_declaration_has_no_version(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: f"{self.default_plugin_id}:",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_declaration_has_no_coordinates(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: f":{self.default_version}",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_declaration_has_no_colon_delimiter(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: "com.plugin.module.1.0.0",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_declaration_is_empty(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: "",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_parse_plugin_when_it_has_id_and_version(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": self.default_version,
                },
            },
        }
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )
        actual_plugins: List[Plugin] = parse_plugins(catalog, versions={}, verbose=False)

        assert actual_plugins == [expected_plugin]

    def test_should_parse_plugin_when_it_has_id_and_reference_to_version(self):
        version_reference: str = f"{self.default_artifact_name}.version"
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": {"ref": version_reference},
                },
            },
        }
        versions: Dict[str, str] = {version_reference: self.default_version}
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )
        actual_plugins: List[Plugin] = parse_plugins(catalog, versions, verbose=False)

        assert actual_plugins == [expected_plugin]

    def test_should_raise_exception_when_there_is_no_plugin_version_by_reference(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": {"ref": "version_reference"},
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_structure_is_incorrect(self):
        catalog: Dict = {
            "plugins": {
                self.default_artifact_name: {
                    "module": self.default_plugin_id,
                    "ref": "version",
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_name_is_not_string(self):
        catalog: Dict = {
            "plugins": {
                42: {
                    "id": self.default_plugin_id,
                    "version": self.default_version,
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_return_empty_libraries_list_when_catalog_has_no_libraries(self):
        catalog: Dict = {"plugins": {}}
        expected_libraries: List[Library] = []
        actual_libraries: List[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == expected_libraries

    def test_should_parse_library_when_it_has_declaration(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: f"{self.default_library_module}:{self.default_version}",
            },
        }
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=self.default_version,
        )
        actual_libraries: List[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_raise_exception_when_library_declaration_has_no_version(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: f"{self.default_library_module}:",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_declaration_has_no_coordinates(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: f":{self.default_version}",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_declaration_has_no_colon_delimiter(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: "com.library.module.1.0.0",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_declaration_is_empty(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: "",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_parse_library_when_it_has_group_name_and_version(self):
        library_group: str = "com.library.group"
        library_name: str = "library-name"
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "group": library_group,
                    "name": library_name,
                    "version": self.default_version,
                },
            },
        }
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=f"{library_group}:{library_name}",
            version=self.default_version,
        )
        actual_libraries: List[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_parse_library_when_it_has_group_name_and_version_reference(self):
        library_group: str = "com.library.group"
        library_name: str = "library-name"
        version_reference: str = f"{self.default_artifact_name}.version"
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "group": library_group,
                    "name": library_name,
                    "version": {"ref": version_reference},
                },
            },
        }
        versions: Dict[str, str] = {version_reference: self.default_version}
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=f"{library_group}:{library_name}",
            version=self.default_version,
        )
        actual_libraries: List[Library] = parse_libraries(catalog, versions, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_raise_exception_when_there_is_library_group_and_name_but_no_version_by_reference(self):
        library_group: str = "com.library.group"
        library_name: str = "library-name"
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "group": library_group,
                    "name": library_name,
                    "version": {"ref": "version_reference"},
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_parse_library_when_it_has_module_and_version(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": self.default_version,
                },
            },
        }
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=self.default_version,
        )
        actual_libraries: List[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_parse_library_when_it_has_module_and_reference_to_version(self):
        version_reference: str = f"{self.default_artifact_name}.version"
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": version_reference},
                },
            },
        }
        versions: Dict[str, str] = {version_reference: self.default_version}
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=self.default_version,
        )
        actual_libraries: List[Library] = parse_libraries(catalog, versions, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_raise_exception_when_there_is_library_module_but_no_version_by_reference(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": "version_reference"},
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_structure_is_incorrect(self):
        catalog: Dict = {
            "libraries": {
                self.default_artifact_name: {
                    "id": self.default_library_module,
                    "ref": "version",
                },
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_name_is_not_string(self):
        catalog: Dict = {
            "libraries": {
                42: "com.library:module:1.0.0",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_return_none_when_there_is_no_repositories(self):
        expected_repositories: Optional[List[Repository]] = None
        actual_repositories: Optional[List[Repository]] = parse_repositories(data={})

        assert actual_repositories == expected_repositories

    def test_should_parse_repository_when_it_has_name_and_address(self):
        data: Dict[str, str] = {
            self.default_repository_name: self.default_repository_address,
        }
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
            user=None,
            password=None,
        )
        actual_repositories: List[Repository] = parse_repositories(data)

        assert actual_repositories == [expected_repository]

    def test_should_parse_repository_when_it_has_name_address_user_and_password(self):
        repository_user: str = "username"
        repository_password: str = "password"
        data: Dict[str, Dict] = {
            self.default_repository_name: {
                "address": self.default_repository_address,
                "user": repository_user,
                "password": repository_password,
            },
        }
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
            user=repository_user,
            password=repository_password,
        )
        actual_repositories: List[Repository] = parse_repositories(data)

        assert actual_repositories == [expected_repository]

    def test_should_raise_exception_when_repository_name_is_not_string(self):
        data: Dict = {
            42: self.default_repository_address,
        }

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_there_is_no_repository_password_but_address_and_user_present(self):
        data: Dict[str, Dict] = {
            self.default_repository_name: {
                "address": self.default_repository_address,
                "user": "username",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_there_is_no_repository_user_but_address_and_password_present(self):
        data: Dict[str, Dict] = {
            self.default_repository_name: {
                "address": self.default_repository_address,
                "password": "password",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_there_is_no_repository_address_but_user_and_password_present(self):
        data: Dict[str, Dict] = {
            self.default_repository_name: {
                "user": "username",
                "password": "password",
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_repository_structure_is_incorrect(self):
        data: List[Tuple] = [("repository_name", "repository_address", "repository_port")]

        with pytest.raises(KatalogerParseException):
            # noinspection PyTypeChecker
            parse_repositories(data)

    def test_should_return_none_when_there_is_no_catalogs(self):
        expected_catalogs: Optional[List[Catalog]] = None
        actual_catalogs: Optional[List[Catalog]] = parse_catalogs(data=[], configuration_root_dir=None)

        assert actual_catalogs == expected_catalogs

    def test_should_parse_unnamed_catalog(self, tmp_catalog: Path):
        data: List[str] = [str(tmp_catalog)]
        expected_catalog: Catalog = Catalog.from_path(tmp_catalog)
        actual_catalogs: Optional[List[Catalog]] = parse_catalogs(data=data, configuration_root_dir=None)

        assert actual_catalogs == [expected_catalog]

    def test_should_raise_exception_when_unnamed_catalog_path_has_incorrect_format(self):
        data: List = [192.168, 0.1]

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_raise_exception_when_unnamed_catalog_has_empty_path(self):
        data: List[str] = [""]

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_parse_named_catalog(self, tmp_catalog: Path):
        data: Dict[str, str] = {
            self.default_catalog_name: str(tmp_catalog),
        }
        expected_catalog: Catalog = Catalog(
            name=self.default_catalog_name,
            path=tmp_catalog,
        )
        actual_catalogs: Optional[List[Catalog]] = parse_catalogs(data, configuration_root_dir=None)

        assert actual_catalogs == [expected_catalog]

    def test_should_raise_exception_when_named_catalog_name_has_incorrect_format(self, tmp_catalog: Path):
        data: Dict = {
            1: str(tmp_catalog),
        }

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_raise_exception_when_named_catalog_path_has_incorrect_format(self, tmp_catalog: Path):
        data: Dict = {
            "catalogs": [str(tmp_catalog)],
        }

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_raise_exception_when_named_catalog_has_empty_name(self, tmp_catalog: Path):
        data: Dict = {
            "": str(tmp_catalog),
        }

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_raise_exception_when_named_catalog_has_empty_path(self):
        data: Dict = {
            self.default_catalog_name: "",
        }

        with pytest.raises(KatalogerParseException):
            parse_catalogs(data, configuration_root_dir=None)

    def test_should_raise_exception_when_catalog_data_format_is_incorrect(self, tmp_catalog: Path):
        with pytest.raises(KatalogerParseException):
            # noinspection PyTypeChecker
            parse_catalogs(data=str(tmp_catalog), configuration_root_dir=None)

    def test_should_load_catalog_from_path(self):
        version_reference: str = f"{self.default_library_module}.version"
        library_version: str = "1.1.1"
        catalog: Dict = {
            "versions": {version_reference: library_version},
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": version_reference},
                },
            },
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": self.default_version,
                },
            },
        }
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=library_version,
        )
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )

        toml_parse_helpers.load_toml = Mock(return_value=catalog)
        actual_libraries, actual_plugins = load_catalog(catalog_path=Mock(), verbose=False)

        assert actual_libraries == [expected_library]
        assert actual_plugins == [expected_plugin]

    def test_should_return_configuration_with_catalogs_when_there_are_catalog_data(self, tmp_catalog: Path):
        configuration_data: Dict = {
            "catalogs": {
                self.default_catalog_name: str(tmp_catalog),
            },
        }
        expected_catalog: Catalog = Catalog(
            name=self.default_catalog_name,
            path=tmp_catalog,
        )

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=[expected_catalog],
            expected_library_repositories=None,
            expected_plugin_repositories=None,
            expected_verbose=None,
            expected_suggest_unstable_updates=None,
            expected_fail_on_updates=None,
        )

    def test_should_return_configuration_with_library_repositories_when_there_are_repositories_data(self):
        configuration_data: Dict = {
            "libraries": {
                self.default_repository_name: self.default_repository_address,
            },
        }
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
        )

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=None,
            expected_library_repositories=[expected_repository],
            expected_plugin_repositories=None,
            expected_verbose=None,
            expected_suggest_unstable_updates=None,
            expected_fail_on_updates=None,
        )

    def test_should_return_configuration_with_plugin_repositories_when_there_are_repositories_data(self):
        configuration_data: Dict = {
            "plugins": {
                self.default_repository_name: self.default_repository_address,
            },
        }
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
        )

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=None,
            expected_library_repositories=None,
            expected_plugin_repositories=[expected_repository],
            expected_verbose=None,
            expected_suggest_unstable_updates=None,
            expected_fail_on_updates=None,
        )

    def test_should_return_configuration_with_verbose_flag_when_it_specified(self):
        verbose_flag: bool = True
        configuration_data: Dict = {
            "verbose": verbose_flag,
        }

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=None,
            expected_library_repositories=None,
            expected_plugin_repositories=None,
            expected_verbose=verbose_flag,
            expected_suggest_unstable_updates=None,
            expected_fail_on_updates=None,
        )

    def test_should_return_configuration_with_suggest_unstable_updates_flag_when_it_specified(self):
        suggest_unstable_updates_flag: bool = False
        configuration_data: Dict = {
            "suggest_unstable_updates": suggest_unstable_updates_flag,
        }

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=None,
            expected_library_repositories=None,
            expected_plugin_repositories=None,
            expected_verbose=None,
            expected_suggest_unstable_updates=suggest_unstable_updates_flag,
            expected_fail_on_updates=None,
        )

    def test_should_return_configuration_with_fail_on_updates_flag_when_it_specified(self):
        fail_on_updates_flag: bool = True
        configuration_data: Dict = {
            "fail_on_updates": fail_on_updates_flag,
        }

        self.__test_load_configuration(
            configuration_data=configuration_data,
            expected_catalogs=None,
            expected_library_repositories=None,
            expected_plugin_repositories=None,
            expected_verbose=None,
            expected_suggest_unstable_updates=None,
            expected_fail_on_updates=fail_on_updates_flag,
        )

    def test_should_raise_exception_when_boolean_flag_has_incorrect_type(self):
        configuration_data: Dict = {
            "verbose": 1,
        }
        toml_parse_helpers.load_toml = Mock(return_value=configuration_data)

        with pytest.raises(KatalogerParseException):
            load_configuration(configuration_path=Mock())

    @staticmethod
    def __test_load_configuration(
        configuration_data: Dict,
        expected_catalogs: Optional[List[Catalog]],
        expected_library_repositories: Optional[List[Repository]],
        expected_plugin_repositories: Optional[List[Repository]],
        expected_verbose: Optional[bool],
        expected_suggest_unstable_updates: Optional[bool],
        expected_fail_on_updates: Optional[bool],
    ):
        expected_configuration: ConfigurationData = ConfigurationData(
            catalogs=expected_catalogs,
            library_repositories=expected_library_repositories,
            plugin_repositories=expected_plugin_repositories,
            verbose=expected_verbose,
            suggest_unstable_updates=expected_suggest_unstable_updates,
            fail_on_updates=expected_fail_on_updates,
        )
        toml_parse_helpers.load_toml = Mock(return_value=configuration_data)
        actual_configuration: ConfigurationData = load_configuration(configuration_path=Mock())

        assert actual_configuration == expected_configuration
