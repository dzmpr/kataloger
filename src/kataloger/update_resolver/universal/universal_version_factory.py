from kataloger.update_resolver.universal.universal_version import UniversalVersion
from kataloger.update_resolver.universal.version_factory import VersionFactory


class UniversalVersionFactory(VersionFactory[UniversalVersion]):

    def create(self, version: str) -> UniversalVersion:
        return UniversalVersion(version)

    def can_create(self, version: str) -> bool:
        return UniversalVersion.can_handle(version)
