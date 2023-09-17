import asyncio

from kataloger.catalog_updater_builder import CatalogUpdaterBuilder
from kataloger.update_resolver.universal.universal_update_resolver import UniversalUpdateResolver
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


def main() -> int:

    async def async_main():
        version_factories = [UniversalVersionFactory()]
        catalog_updater = (CatalogUpdaterBuilder()
                           .set_repositories_path("./default.repositories.toml")
                           .add_resolver(UniversalUpdateResolver(version_factories))
                           .set_verbose(verbose=True)
                           .build())
        path_to_catalog = "./catalog.versions.toml"
        updates = await catalog_updater.get_catalog_updates(path_to_catalog)
        for update in updates:
            print(update)

        return min(1, len(updates))  # Non-zero return code if we found updates

    return asyncio.run(async_main())


if __name__ == "__main__":
    import sys
    sys.exit(main())
