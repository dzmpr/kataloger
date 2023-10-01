from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KatalogerConfiguration:
    path_to_catalog: Path  # TODO: support multiple catalogs update
    path_to_repositories: Path  # TODO: support bundling default configuration
    verbose: bool = False
    suggest_unstable_updates: bool = False
    fail_on_updates: bool = False
