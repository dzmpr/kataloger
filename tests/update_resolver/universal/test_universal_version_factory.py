from kataloger.update_resolver.universal.universal_version import UniversalVersion
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


class TestUniversalVersionFactory:
    def test_create_should_return_universal_version_for_provided_version_string(self):
        version_string: str = "1.2.3-alpha01"
        version: UniversalVersion = self._create_factory().create(version_string)

        assert version_string == version.raw

    def test_try_create_should_return_false_when_version_string_does_not_match_universal_version_regexp(self):
        version_string: str = "RELEASE131"
        can_create_version: bool = self._create_factory().can_create(version_string)

        assert not can_create_version

    def test_try_create_should_return_true_when_version_string_does_match_universal_version_regexp(self):
        version_string: str = "1.2.3-alpha01"
        can_create_version: bool = self._create_factory().can_create(version_string)

        assert can_create_version

    @staticmethod
    def _create_factory() -> UniversalVersionFactory:
        return UniversalVersionFactory()
