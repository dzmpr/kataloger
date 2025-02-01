from dataclasses import dataclass
from typing import Optional

from kataloger.data.catalog import Catalog
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class ConfigurationData:
    catalogs: Optional[list[Catalog]]
    library_repositories: Optional[list[Repository]]
    plugin_repositories: Optional[list[Repository]]
    verbose: Optional[bool]
    suggest_unstable_updates: Optional[bool]
    fail_on_updates: Optional[bool]
