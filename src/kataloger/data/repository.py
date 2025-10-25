from dataclasses import dataclass

from yarl import URL


@dataclass(frozen=True)
class Repository:
    name: str
    address: URL
    user: str | None = None
    password: str | None = None

    def __repr__(self):
        return self.name

    def requires_authorization(self) -> bool:
        return self.user is not None and self.password is not None
