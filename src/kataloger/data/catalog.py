from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from kataloger.helpers.backport_helpers import remove_suffix


@dataclass(frozen=True)
class Catalog:
    name: Optional[str]
    path: Path

    @staticmethod
    def from_path(path: Path) -> "Catalog":
        return Catalog(
            name=remove_suffix(path.name, ".versions.toml"),
            path=path,
        )
