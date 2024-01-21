from kataloger.catalog_updater_builder import CatalogUpdaterBuilder
from kataloger.cli.configuration_provider import parse_configuration
from kataloger.cli.update_print_helper import print_catalog_updates
from kataloger.update_resolver.universal.universal_update_resolver import UniversalUpdateResolver
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


async def run() -> int:
    configuration = parse_configuration()

    update_resolver = UniversalUpdateResolver(
        version_factories=[UniversalVersionFactory()],
        suggest_unstable_updates=configuration.suggest_unstable_updates,
    )

    catalog_updater = (CatalogUpdaterBuilder()
                       .add_resolver(update_resolver)
                       .set_repositories_path(configuration.repositories_path)
                       .set_verbose(verbose=configuration.verbose)
                       .build())

    has_updates = False
    for catalog_path in configuration.catalogs:
        updates = await catalog_updater.get_catalog_updates(catalog_path)
        if not has_updates and updates:
            has_updates = True

        print_catalog_updates(
            updates=updates,
            catalog_name=catalog_path.name,
            catalog_count=len(configuration.catalogs),
            verbose=configuration.verbose,
        )

    if configuration.fail_on_updates and has_updates:
        return 1
    else:
        return 0
