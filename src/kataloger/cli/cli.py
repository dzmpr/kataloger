from kataloger.catalog_updater import CatalogUpdater
from kataloger.cli.configuration_provider import get_configuration
from kataloger.cli.update_print_helper import print_catalog_updates
from kataloger.update_resolver.universal.universal_update_resolver import UniversalUpdateResolver
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


async def run() -> int:
    configuration = get_configuration()

    update_resolver = UniversalUpdateResolver(
        version_factories=[UniversalVersionFactory()],
        suggest_unstable_updates=configuration.suggest_unstable_updates,
    )

    catalog_updater = CatalogUpdater(
        library_repositories=configuration.library_repositories,
        plugin_repositories=configuration.plugin_repositories,
        update_resolvers=[update_resolver],
        verbose=configuration.verbose,
    )

    has_updates = False
    for catalog in configuration.catalogs:
        updates = await catalog_updater.get_catalog_updates(catalog.path)
        if not has_updates and updates:
            has_updates = True

        print_catalog_updates(
            updates=updates,
            catalog_name=catalog.name,
            catalog_count=len(configuration.catalogs),
            verbose=configuration.verbose,
        )

    if configuration.fail_on_updates and has_updates:
        return 1
    return 0
