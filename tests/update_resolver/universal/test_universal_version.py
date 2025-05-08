from kataloger.update_resolver.universal.universal_version import UniversalVersion


class TestUniversalVersion:
    def test_can_handle_should_return_true_for_version_formats_that_can_be_parsed(self):
        correct_versions: list[str] = [
            "1.2.3.4.5.6.7.8.9.0.1.2.3.4.5.6.7.8.9.0.1",  # Version with max numeric components
            "1.1.1",  # Semver version
            "00.00.02",  # Version with multiple zeros components
            "10",  # Single integer version
            "23.40",  # Two components version
            "1.2.3-alpha03",  # Google version format
            "1.8.1.300",  # Huawei version format
            "1.9.0-Beta",  # Version with uppercase in pre-release part
            "16.4.2-pre.49",  # Version with delimiter in pre-release part
            "2.5.1-payscompat01",  # Version with custom pre-release part
            "1.3.10.alpha10",  # Version with 'dot' pre-release separator
        ]
        for version in correct_versions:
            assert UniversalVersion.can_handle(version)

    def test_can_handle_should_return_false_for_version_formats_that_cant_be_parsed(self):
        incorrect_versions: list[str] = [
            "0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.1",  # Too much numeric components
            "RELEASE130",  # Word-prefixed version
            "v1.3.0",  # v-prefix
            "1.3.0dev",  # Symbols in numeric part / no pre-release divider
            "1.8.20.",  # Version with trailing dot / missing numeric component
        ]
        for version in incorrect_versions:
            assert not UniversalVersion.can_handle(version)

    def test_is_pre_release_should_return_true_when_version_has_pre_release_postfix(self):
        versions: list[str] = [
            "1.2.3-alpha03",
            "1.9.0-Beta",
            "16.4.2-pre.49",
            "16.4.2-pre-50",
            "2.5.1-compcompat01",
            "1.3.10.alpha10",
        ]
        for version in versions:
            assert UniversalVersion(version).is_pre_release()

    def test_is_pre_release_should_return_false_when_version_has_no_pre_release_postfix(self):
        versions: list[str] = [
            "1.2.3",
            "131",
            "10.20",
        ]
        for version in versions:
            assert not UniversalVersion(version).is_pre_release()

    def test_pre_release_number_should_be_extracted_as_int_from_version_if_pre_release_part_contains_number(self):
        versions_to_numbers: dict[str, int] = {
            "1.2.3-alpha1": 1,
            "1.2.3-rc003": 3,
            "1.2.3-beta.4": 4,
        }
        for version, expected_pre_release_number in versions_to_numbers.items():
            assert UniversalVersion(version).pre_release_number == expected_pre_release_number

    def test_pre_release_number_should_be_extracted_as_0_from_version_if_pre_release_part_not_contains_number(self):
        versions: list[str] = [
            "1.2.3",
            "1.2.3-beta",
        ]
        expected_pre_release_number = 0
        for version in versions:
            assert UniversalVersion(version).pre_release_number == expected_pre_release_number

    def test_versions_with_same_number_should_be_compared_case_insensitively_by_pre_release_name(self):
        versions: list[str] = [
            "1.2.3-unexpected-pre-release-name01",
            "1.2.3-dev01",
            "1.2.3-alPha01",
            "1.2.3-Beta01",
            "1.2.3-RC01",
        ]
        sorted_versions: list[UniversalVersion] = sorted(UniversalVersion(v) for v in versions)
        for expected, actual in zip(versions, sorted_versions):
            assert actual.raw == expected

    def test_versions_should_considered_as_equal_when_version_string_representations_are_equals(self):
        first_version: UniversalVersion = UniversalVersion("1.2.3-pre-release-name-005")
        second_version: UniversalVersion = UniversalVersion("1.2.3-pre-release-name-005")
        assert first_version == second_version

    def test_versions_should_not_considered_as_equal_when_version_string_representations_are_not_equals(self):
        first_version: UniversalVersion = UniversalVersion("1.2.3-pre-release-name-005")
        second_version: UniversalVersion = UniversalVersion("1.2.3-pre-release-name-05")
        assert first_version != second_version

    def test_version_should_considered_not_equal_for_any_non_universal_version_type(self):
        version: UniversalVersion = UniversalVersion("1.2.3")
        comparing_objects: list[object] = [
            "1.2.3",
            None,
            True,
        ]
        for obj in comparing_objects:
            assert obj != version

    def test_each_numeric_version_component_should_be_compared_with_corresponding_component_numerically(self):
        versions: list[tuple[str, str, bool]] = [
            ("1.2.3", "1.2.3", False),
            ("0.0.0", "0.0.1", True),
            ("1.1.3", "1.2.3", True),
            ("0.2.3", "1.0.0", True),
            ("1.2.3", "1.2.30", True),
            ("1.2.03", "1.2.3", False),
        ]
        self._version_comparison_test(versions)

    def test_missing_numeric_components_due_comparison_should_be_considered_as_zero(self):
        versions: list[tuple[str, str, bool]] = [
            ("1.0.0", "1", False),
            ("1.0.1", "1", False),
            ("1.0.0.0.0", "1.0.0.0.1", True),
            ("2.3", "2.3.4", True),
        ]
        self._version_comparison_test(versions)

    def test_should_considered_less_than_not_pre_release_version_when_numeric_parts_are_equal_pre_release_version(self):
        versions: list[tuple[str, str, bool]] = [
            ("1.0.0-alpha", "1.0.0", True),
            ("1.0.0-beta01", "1.0.0", True),
            ("1.0.0-some-pre-release", "1.0.0", True),
        ]
        self._version_comparison_test(versions)

    def test_should_compare_by_pre_release_numbers_when_numeric_parts_and_pre_release_names_are_equal(self):
        versions: list[tuple[str, str, bool]] = [
            ("1.0.0-alpha01", "1.0.0-alpha02", True),
            ("1.0.0-alpha01", "1.0.0-alpha2", True),
            ("1.0.0-alpha100", "1.0.0-alpha101", True),
            ("1.0.0-alpha100", "1.0.0-alpha1", False),
        ]
        self._version_comparison_test(versions)

    def test_should_compare_by_pre_release_index_when_numeric_parts_are_equal_and_pre_release_names_are_not_equal(self):
        versions: list[tuple[str, str, bool]] = [
            ("1.0.0-alpha", "1.0.0-beta100", True),
            ("1.0.0-dev", "1.0.0-rc100", True),
            ("1.0.0-beta", "1.0.0-rc100", True),
            ("1.0.0-rc100", "1.0.0-dev100", False),
        ]
        self._version_comparison_test(versions)

    @staticmethod
    def _version_comparison_test(data: list[tuple[str, str, bool]]):
        for first_version, second_version, expected_result in data:
            actual_result = UniversalVersion(first_version) < UniversalVersion(second_version)
            assert actual_result == expected_result
