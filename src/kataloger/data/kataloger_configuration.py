from dataclasses import dataclass

from kataloger.data.catalog import Catalog
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class KatalogerConfiguration:
    catalogs: list[Catalog]
    library_repositories: list[Repository]
    plugin_repositories: list[Repository]
    verbose: bool
    suggest_unstable_updates: bool
    fail_on_updates: bool
