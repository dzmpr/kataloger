from dataclasses import dataclass
from typing import List

from kataloger.data.catalog import Catalog
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class KatalogerConfiguration:
    catalogs: List[Catalog]
    library_repositories: List[Repository]
    plugin_repositories: List[Repository]
    verbose: bool
    suggest_unstable_updates: bool
    fail_on_updates: bool
