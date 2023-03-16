class AvailableUpdate:
    def __init__(
        self,
        artifact_name: str,
        repository_name: str,
        current_version: str,
        available_version: str,
    ):
        self.artifact_name = artifact_name
        self.repository_name = repository_name
        self.current_version = current_version
        self.available_version = available_version
