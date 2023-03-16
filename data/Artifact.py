from abc import ABC, abstractmethod


class Artifact(ABC):
    def __init__(self, name: str | None, coordinates: str, version: str):
        self.name = name
        self.coordinates = coordinates
        self.version = version

    @abstractmethod
    def to_path(self) -> str:
        pass
