from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Catalog:
    name: str | None
    path: Path

    @staticmethod
    def from_path(path: Path) -> "Catalog":
        return Catalog(
            name=path.name.removesuffix(".versions.toml"),
            path=path,
        )
