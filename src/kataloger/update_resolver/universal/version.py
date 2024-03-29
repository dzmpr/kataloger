from abc import ABC, abstractmethod


class Version(ABC):
    def __init__(self, raw: str):
        self.raw = raw

    def __repr__(self):
        return self.raw

    @abstractmethod
    def is_pre_release(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __lt__(self, other: object) -> bool:
        raise NotImplementedError
