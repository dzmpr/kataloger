from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Artifact(ABC):
    name: str | None
    coordinates: str
    version: str

    def __repr__(self):
        return self.name

    @abstractmethod
    def to_path(self) -> str:
        pass
