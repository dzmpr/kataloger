from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Catalog:
    name: Optional[str]
    path: Path

    @staticmethod
    def from_path(path: Path) -> "Catalog":
        return Catalog(
            name=path.name.removesuffix(".versions.toml"),
            path=path,
        )
