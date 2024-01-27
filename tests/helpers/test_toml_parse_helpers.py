from unittest.mock import Mock, patch, mock_open

import pytest
from yarl import URL

from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.repository import Repository
from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException
from kataloger.helpers import toml_parse_helpers
from kataloger.helpers.toml_parse_helpers import parse_plugins, parse_libraries, parse_repositories, \
    load_toml_to_dict, load_repositories, load_catalog


class TestTomlParseHelpers:
    default_artifact_name = "artifact_name"
    default_plugin_id = "com.plug.in"
    default_library_module = "com.library:library-core"
    default_version = "1.0.0"
    default_repository_name = "repository_name"
    default_repository_address = "https://reposito.ry/"

    def test_should_read_toml_file_to_dictionary_when_toml_format_is_correct(self):
        toml: bytes = b"""\
        [versions]
        hilt = "2.50"
        
        [libraries]
        kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version = "1.9.22" }
        """
        expected_data: dict = {
            "versions": {
                "hilt": "2.50"
            },
            "libraries": {
                "kotlin-stdlib": {
                    "module": "org.jetbrains.kotlin:kotlin-stdlib",
                    "version": "1.9.22",
                }
            },
        }
        with patch("builtins.open", mock_open(read_data=toml)):
            actual_data: dict = load_toml_to_dict(path=Mock())

        assert actual_data == expected_data

    def test_should_raise_exception_when_toml_format_is_incorrect(self):
        toml: bytes = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>"""
        with patch("builtins.open", mock_open(read_data=toml)):
            with pytest.raises(KatalogerParseException):
                load_toml_to_dict(path=Mock())

    def test_should_return_empty_plugins_list_when_catalog_has_no_plugins(self):
        catalog: dict = {"libraries": {}}
        expected_plugins: list[Plugin] = []
        actual_plugins: list[Plugin] = parse_plugins(catalog, versions={}, verbose=False)

        assert actual_plugins == expected_plugins

    def test_should_parse_plugin_when_it_has_id_and_version(self):
        catalog: dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": self.default_version,
                }
            },
        }
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )
        actual_plugins: list[Plugin] = parse_plugins(catalog, versions={}, verbose=False)

        assert actual_plugins == [expected_plugin]

    def test_should_parse_plugin_when_it_has_id_and_reference_to_version(self):
        version_reference: str = f"{self.default_artifact_name}.version"
        catalog: dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": {"ref": version_reference},
                }
            },
        }
        versions: dict[str, str] = {version_reference: self.default_version}
        expected_plugin: Plugin = Plugin(
            name=self.default_artifact_name,
            coordinates=self.default_plugin_id,
            version=self.default_version,
        )
        actual_plugins: list[Plugin] = parse_plugins(catalog, versions, verbose=False)

        assert actual_plugins == [expected_plugin]

    def test_should_raise_exception_when_there_is_no_plugin_version_by_reference(self):
        catalog: dict = {
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": {"ref": "version_reference"},
                }
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_plugin_structure_is_incorrect(self):
        catalog: dict = {
            "plugins": {
                self.default_artifact_name: {
                    "module": self.default_plugin_id,
                    "ref": "version",
                }
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_plugins(catalog, versions={}, verbose=False)

    def test_should_return_empty_libraries_list_when_catalog_has_no_libraries(self):
        catalog: dict = {"plugins": {}}
        expected_libraries: list[Library] = []
        actual_libraries: list[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == expected_libraries

    def test_should_parse_library_when_it_has_module_and_version(self):
        catalog: dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": self.default_version,
                }
            },
        }
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=self.default_version,
        )
        actual_libraries: list[Library] = parse_libraries(catalog, versions={}, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_parse_library_when_it_has_module_and_reference_to_version(self):
        version_reference: str = f"{self.default_artifact_name}.version"
        catalog: dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": version_reference},
                }
            },
        }
        versions: dict[str, str] = {version_reference: self.default_version}
        expected_library: Library = Library(
            name=self.default_artifact_name,
            coordinates=self.default_library_module,
            version=self.default_version,
        )
        actual_libraries: list[Library] = parse_libraries(catalog, versions, verbose=False)

        assert actual_libraries == [expected_library]

    def test_should_raise_exception_when_there_is_no_library_version_by_reference(self):
        catalog: dict = {
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": "version_reference"},
                }
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_raise_exception_when_library_structure_is_incorrect(self):
        catalog: dict = {
            "libraries": {
                self.default_artifact_name: {
                    "id": self.default_library_module,
                    "ref": "version",
                }
            },
        }

        with pytest.raises(KatalogerParseException):
            parse_libraries(catalog, versions={}, verbose=False)

    def test_should_return_empty_repositories_list_when_there_is_no_repositories(self):
        expected_repositories: list[Repository] = []
        actual_repositories: list[Repository] = parse_repositories(repositories_data=[])

        assert actual_repositories == expected_repositories

    def test_should_parse_repository_when_it_has_name_and_address(self):
        data: list[tuple[str, str]] = [
            (self.default_repository_name, self.default_repository_address),
        ]
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
            user=None,
            password=None,
        )
        actual_repositories: list[Repository] = parse_repositories(data)

        assert actual_repositories == [expected_repository]

    def test_should_parse_repository_when_it_has_name_address_user_and_password(self):
        repository_user: str = "username"
        repository_password: str = "password"
        data: list[tuple] = [
            (
                self.default_repository_name, {
                    "address": self.default_repository_address,
                    "user": repository_user,
                    "password": repository_password,
                },
            )
        ]
        expected_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
            user=repository_user,
            password=repository_password,
        )
        actual_repositories: list[Repository] = parse_repositories(data)

        assert actual_repositories == [expected_repository]

    def test_should_raise_exception_when_there_is_no_repository_user_but_password_present(self):
        data: list[tuple] = [
            (
                self.default_repository_name, {
                    "address": self.default_repository_address,
                    "user": "username",
                },
            )
        ]

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_there_is_no_repository_password_but_user_present(self):
        data: list[tuple] = [
            (
                self.default_repository_name, {
                    "address": self.default_repository_address,
                    "password": "password",
                },
            )
        ]

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_raise_exception_when_repository_structure_is_incorrect(self):
        data: list[tuple] = [("repository_name", "repository_address", "repository_port")]

        with pytest.raises(KatalogerParseException):
            parse_repositories(data)

    def test_should_load_catalog_from_path(self):
        version_reference: str = f"{self.default_library_module}.version"
        library_version: str = "1.1.1"
        catalog: dict = {
            "versions": {version_reference: library_version},
            "libraries": {
                self.default_artifact_name: {
                    "module": self.default_library_module,
                    "version": {"ref": version_reference},
                }
            },
            "plugins": {
                self.default_artifact_name: {
                    "id": self.default_plugin_id,
                    "version": self.default_version,
                }
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

        toml_parse_helpers.load_toml_to_dict = Mock(return_value=catalog)
        actual_libraries, actual_plugins = load_catalog(catalog_path=Mock(), verbose=False)

        assert actual_libraries == [expected_library]
        assert actual_plugins == [expected_plugin]

    def test_should_load_repositories_from_path(self):
        repository_user: str = "username"
        repository_password: str = "password"
        repository_data: dict = {
            "libraries": {
                self.default_repository_name: self.default_repository_address,
            },
            "plugins": {
                self.default_repository_name: {
                    "address": self.default_repository_address,
                    "user": repository_user,
                    "password": repository_password,
                },
            }
        }
        expected_library_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
        )
        expected_plugin_repository: Repository = Repository(
            name=self.default_repository_name,
            address=URL(self.default_repository_address),
            user=repository_user,
            password=repository_password,
        )
        toml_parse_helpers.load_toml_to_dict = Mock(return_value=repository_data)
        actual_library_repositories, actual_plugin_repositories = load_repositories(Mock())

        assert actual_library_repositories == [expected_library_repository]
        assert actual_plugin_repositories == [expected_plugin_repository]
