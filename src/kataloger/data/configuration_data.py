from dataclasses import dataclass
from typing import List, Optional

from kataloger.data.catalog import Catalog
from kataloger.data.repository import Repository


@dataclass(frozen=True)
class ConfigurationData:
    catalogs: Optional[List[Catalog]]
    library_repositories: Optional[List[Repository]]
    plugin_repositories: Optional[List[Repository]]
    verbose: Optional[bool]
    suggest_unstable_updates: Optional[bool]
    fail_on_updates: Optional[bool]
