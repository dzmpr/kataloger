from dataclasses import dataclass

from kataloger.data.catalog import Catalog
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class ConfigurationData:
    catalogs: list[Catalog] | None
    library_repositories: list[Repository] | None
    plugin_repositories: list[Repository] | None
    verbose: bool | None
    suggest_unstable_updates: bool | None
    fail_on_updates: bool | None
