from dataclasses import dataclass


@dataclass
class ArtifactUpdate:
    name: str
    update_repository_name: str
    current_version: str
    available_version: str

    def __repr__(self):
        return f"{self.name} {self.current_version} -> {self.available_version}"
