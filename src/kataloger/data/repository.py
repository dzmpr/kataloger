from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Repository:
    name: str
    address: str
    user: Optional[str] = None
    password: Optional[str] = None

    def __repr__(self):
        return self.name

    def requires_authorization(self) -> bool:
        return self.user is not None and self.password is not None
