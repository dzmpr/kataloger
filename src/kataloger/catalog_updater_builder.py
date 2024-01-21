from pathlib import Path
from typing import Optional, Self

from kataloger.catalog_updater import CatalogUpdater
from kataloger.data.repository import Repository
from kataloger.execptions.kataloger_configuration_exception import KatalogerConfigurationException
from kataloger.helpers.toml_parse_helpers import load_repositories
from kataloger.update_resolver.base.update_resolver import UpdateResolver


class CatalogUpdaterBuilder:

    def __init__(self):
        self.repositories_path: Optional[Path] = None
        self.library_repositories: list[Repository] = []
        self.plugin_repositories: list[Repository] = []
        self.update_resolvers: list[UpdateResolver] = []
        self.verbose: bool = False

    def set_repositories_path(self, path: Path) -> Self:
        if not (path.exists() and path.is_file()):
            raise KatalogerConfigurationException(message=f"Incorrect path to repositories: {path}.")

        self.repositories_path = path
        return self

    def set_library_repositories(self, repositories: list[Repository]) -> Self:
        self.library_repositories = repositories
        return self

    def set_plugin_repositories(self, repositories: list[Repository]) -> Self:
        self.plugin_repositories = repositories
        return self

    def set_resolvers(self, resolvers: list[UpdateResolver]) -> Self:
        self.update_resolvers = resolvers
        return self

    def add_resolver(self, resolver: UpdateResolver) -> Self:
        self.update_resolvers.append(resolver)
        return self

    def set_verbose(self, verbose: bool) -> Self:
        self.verbose = verbose
        return self

    def build(self) -> CatalogUpdater:
        if path := self.repositories_path:
            (library_repos, plugin_repos) = load_repositories(path)
            self.library_repositories.extend(library_repos)
            self.plugin_repositories.extend(plugin_repos)

        return CatalogUpdater(
            library_repositories=self.library_repositories,
            plugin_repositories=self.plugin_repositories,
            update_resolvers=self.update_resolvers,
            verbose=self.verbose,
        )
