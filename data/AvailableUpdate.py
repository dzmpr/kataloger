class AvailableUpdate:
    def __init__(self, artifact_id: str, current_version: str, available_version: str):
        self.artifact_id = artifact_id
        self.current_version = current_version
        self.available_version = available_version
