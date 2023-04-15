from data.ArtifactMetadata import ArtifactMetadata


class ArtifactUpdateInfo:
    def __init__(
        self,
        artifact_name: str,
        current_version: str,
        update_candidates: list[ArtifactMetadata],
    ):
        self.artifact_name = artifact_name
        self.current_version = current_version
        self.update_candidates = update_candidates
