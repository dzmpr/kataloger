from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KatalogerConfiguration:
    catalogs: list[Path]
    repositories_path: Path
    verbose: bool = False
    suggest_unstable_updates: bool = False
    fail_on_updates: bool = False
