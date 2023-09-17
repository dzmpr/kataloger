from dataclasses import dataclass
from functools import total_ordering


@dataclass(frozen=True)
@total_ordering
class ArtifactMetadata:
    latest_version: str
    release_version: str
    versions: list[str]
    last_updated: int

    def __repr__(self):
        return f"{len(self.versions)}/{self.latest_version}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, ArtifactMetadata):
            return False

        return self.last_updated == other.last_updated

    def __lt__(self, other) -> bool:
        if not isinstance(other, ArtifactMetadata):
            return False

        return self.last_updated == other.last_updated
