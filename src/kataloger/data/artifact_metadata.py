from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactMetadata:
    latest_version: str
    release_version: str
    versions: list[str]
    last_updated: int

    def __repr__(self):
        return f"{len(self.versions)}/{self.latest_version}"
