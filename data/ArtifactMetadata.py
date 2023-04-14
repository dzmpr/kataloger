from data.Repository import Repository


class ArtifactMetadata:
    def __init__(
        self,
        repository: Repository,
        latest_version: str,
        release_version: str,
        versions: list[str],
    ):
        self.repository = repository
        self.latest_version = latest_version
        self.release_version = release_version
        self.versions = versions
