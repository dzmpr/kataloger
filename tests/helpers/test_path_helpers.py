from pathlib import Path

import pytest

from kataloger.exceptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.helpers.path_helpers import file_exists, str_to_path


class TestPathHelpers:
    def test_should_return_path_when_path_string_is_correct_and_file_exists(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"
        file_path.touch()
        actual_path: Path = str_to_path(str(file_path))

        assert file_path == actual_path

    def test_should_raise_exception_when_path_string_is_correct_but_file_not_exists(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"

        with pytest.raises(KatalogerConfigurationException):
            str_to_path(str(file_path))

    def test_should_resolve_relative_path_to_the_root_and_return_resolved_path(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"
        file_path.touch()
        root_path: Path = tmp_path.parent
        relative_file_path: Path = file_path.relative_to(root_path)

        actual_path: Path = str_to_path(path_string=str(relative_file_path), root_path=root_path)

        assert file_path == actual_path

    def test_should_raise_exception_when_relative_path_is_correct_but_file_not_exists(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"
        root_path: Path = tmp_path.parent
        relative_file_path: Path = file_path.relative_to(root_path)

        with pytest.raises(KatalogerConfigurationException):
            str_to_path(path_string=str(relative_file_path), root_path=root_path)

    def test_should_raise_exception_when_relative_path_provided_without_root_and_cant_be_resolved(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"
        file_path.touch()
        root_path: Path = tmp_path.parent
        relative_file_path: Path = file_path.relative_to(root_path)

        with pytest.raises(KatalogerConfigurationException):
            str_to_path(path_string=str(relative_file_path), root_path=None)

    def test_should_return_true_when_path_exists_and_its_file(self, tmp_path: Path):
        file_path: Path = tmp_path / "file.txt"
        file_path.touch()

        assert file_exists(file_path)

    def test_should_return_false_when_path_exists_but_its_not_file(self, tmp_path: Path):
        assert not file_exists(tmp_path)

    def test_should_return_false_when_path_not_exists(self, tmp_path: Path):
        path: Path = tmp_path / "non_existing_directory"
        assert not file_exists(path)
