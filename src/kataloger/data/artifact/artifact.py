from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Artifact(ABC):
    name: Optional[str]
    coordinates: str
    version: str

    def __repr__(self):
        return self.name

    @abstractmethod
    def to_path(self) -> str:
        pass
