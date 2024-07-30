from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from kataloger.exceptions.kataloger_parse_exception import KatalogerParseException
from kataloger.helpers.backport_helpers import load_toml, remove_suffix


class TestBackportHelpers:

    def test_should_remove_string_suffix_when_string_ends_with_provided_suffix(self):
        initial_string: str = "some string"
        suffix: str = "string"

        assert remove_suffix(initial_string, suffix) == "some "

    def test_should_return_string_as_is_when_string_not_ends_with_provided_suffix(self):
        initial_string: str = "some string"
        suffix: str = "integer"

        assert remove_suffix(initial_string, suffix) == initial_string

    def test_should_read_toml_file_to_dictionary_when_toml_format_is_correct(self):
        toml: bytes = b"""\
        [versions]
        hilt = "2.50"

        [libraries]
        kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version = "1.9.22" }
        """
        expected_data: dict = {
            "versions": {
                "hilt": "2.50",
            },
            "libraries": {
                "kotlin-stdlib": {
                    "module": "org.jetbrains.kotlin:kotlin-stdlib",
                    "version": "1.9.22",
                },
            },
        }
        with patch.object(Path, "open", mock_open(read_data=toml)):
            actual_data: dict = load_toml(path=Mock())

        assert actual_data == expected_data

    def test_should_raise_exception_when_toml_format_is_incorrect(self):
        toml: bytes = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>"""
        with patch.object(Path, "open", mock_open(read_data=toml)), pytest.raises(KatalogerParseException):
            load_toml(path=Mock())
