from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ArtifactMetadata:
    latest_version: str
    release_version: str
    versions: List[str]
    last_updated: int

    def __repr__(self):
        return f"{len(self.versions)}/{self.latest_version}"
