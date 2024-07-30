from typing import Dict, List

import pytest

from kataloger.helpers.structural_matching_helpers import match


class TestStructuralMatchingHelpers:
    default_key: str = "password"
    default_value: str = "12345678"

    def test_pattern_should_match_data_when_data_has_same_object_as_value(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: self.default_value}

        assert match(data, pattern)

    def test_pattern_should_not_match_data_when_data_has_different_object_as_value(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: "qwerty"}

        assert match(data, pattern) is None

    def test_pattern_should_match_data_when_data_has_value_of_type_specified_in_pattern(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: str}

        assert match(data, pattern)

    def test_pattern_should_not_match_data_when_data_has_value_of_different_type_than_specified_in_pattern(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: int}

        assert not match(data, pattern)

    def test_should_match_data_with_dictionary_values(self):
        data: Dict = {"credentials": {self.default_key: self.default_value}}
        pattern: Dict = {"credentials": {self.default_key: self.default_value}}

        assert match(data, pattern)

    def test_match_result_should_contain_value_from_data_accessible_with_key_from_pattern(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: self.default_value}

        mr = match(data, pattern)
        assert mr is not None
        assert getattr(mr, self.default_key) == self.default_value

    def test_match_result_should_contain_nested_match_result_for_dictionary_values(self):
        top_level_key: str = "credentials"
        data: Dict = {top_level_key: {self.default_key: self.default_value}}
        pattern: Dict = {top_level_key: {self.default_key: self.default_value}}

        mr = match(data, pattern)
        assert mr is not None
        nested_mr = getattr(mr, top_level_key)
        assert nested_mr == match(data[top_level_key], pattern[top_level_key])
        assert getattr(nested_mr, self.default_key) == self.default_value

    def test_match_should_raise_value_error_when_pattern_key_is_a_type(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {str: self.default_value}

        with pytest.raises(ValueError, match="Can't use types as pattern keys:.*"):
            match(data, pattern)

    def test_should_return_none_when_pattern_is_not_dictionary(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: List = [self.default_key, self.default_value]

        # noinspection PyTypeChecker
        assert not match(data, pattern)

    def test_should_return_none_when_data_is_not_dictionary(self):
        data: List = [self.default_key, self.default_value]
        pattern: Dict = {self.default_key: self.default_value}

        # noinspection PyTypeChecker
        assert not match(data, pattern)

    def test_should_return_none_when_data_has_more_items_than_pattern(self):
        data: Dict = {self.default_key: self.default_value, "extra": 42}
        pattern: Dict = {self.default_key: self.default_value}

        assert not match(data, pattern)

    def test_should_return_none_when_pattern_has_more_items_than_data(self):
        data: Dict = {self.default_key: self.default_value}
        pattern: Dict = {self.default_key: self.default_value, "extra": 42}

        assert not match(data, pattern)

    def test_should_return_none_when_one_of_keys_in_pattern_are_missing_in_data(self):
        data: Dict = {self.default_key: self.default_value, "key": 42}
        pattern: Dict = {self.default_key: self.default_value, "extra": 42}

        assert not match(data, pattern)

    def test_should_treat_lists_and_tuples_as_value_in_pattern(self):
        assert match(data={"data": [42]}, pattern={"data": [42]})
        assert not match(data={"data": [42]}, pattern={"data": [int]})

        assert match(data={"data": (42,)}, pattern={"data": (42,)})
        assert not match(data={"data": (42,)}, pattern={"data": (int,)})
