from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from kataloger.update_resolver.universal.version import Version

T = TypeVar("T", bound=Version)


class VersionFactory(ABC, Generic[T]):

    @abstractmethod
    def create(self, version: str) -> T:
        raise NotImplementedError

    @abstractmethod
    def can_create(self, version: str) -> bool:
        raise NotImplementedError
