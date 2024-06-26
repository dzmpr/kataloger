from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Catalog:
    name: Optional[str]
    path: Path

    @staticmethod
    def from_path(path: Path) -> "Catalog":
        catalog_name = path.name.removesuffix(".versions.toml") if path.name.endswith(".versions.toml") else path.name
        return Catalog(
            name=catalog_name,
            path=path,
        )
