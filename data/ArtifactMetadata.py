class ArtifactMetadata:
    def __init__(self, latest_version: str, release_version: str, versions: list[str]):
        self.latest_version = latest_version
        self.release_version = release_version
        self.versions = versions
