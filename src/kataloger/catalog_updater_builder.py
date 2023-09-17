from typing import Optional, Self

from kataloger.catalog_updater import CatalogUpdater
from kataloger.data.repository import Repository
from kataloger.helpers.toml_parse_helpers import load_repositories
from kataloger.update_resolver.base.update_resolver import UpdateResolver


class CatalogUpdaterBuilder:

    repositories_path: Optional[str] = None
    library_repositories: list[Repository] = []
    plugin_repositories: list[Repository] = []
    update_resolvers: list[UpdateResolver] = []
    verbose: bool = False

    def set_repositories_path(self, path: str) -> Self:
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
        # TODO: Safely handle None repositories_path
        if path := self.repositories_path.strip():
            (library_repos, plugin_repos) = load_repositories(path)
            self.library_repositories.extend(library_repos)
            self.plugin_repositories.extend(plugin_repos)

        return CatalogUpdater(
            self.library_repositories,
            self.plugin_repositories,
            self.update_resolvers,
            self.verbose,
        )
