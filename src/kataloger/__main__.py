import sys
from pathlib import Path

import asyncio

from kataloger.catalog_updater_builder import CatalogUpdaterBuilder
from kataloger.execptions.kataloger_exception import KatalogerException
from kataloger.update_resolver.universal.universal_update_resolver import UniversalUpdateResolver
from kataloger.update_resolver.universal.universal_version_factory import UniversalVersionFactory


def main() -> int:

    async def async_main():
        try:
            path_to_repositories = "./default.repositories.toml"
            path_to_catalog = "./catalog.versions.toml"
            version_factories = [UniversalVersionFactory()]
            catalog_updater = (CatalogUpdaterBuilder()
                               .set_repositories_path(Path(path_to_repositories))
                               .add_resolver(UniversalUpdateResolver(version_factories))
                               .set_verbose(verbose=True)
                               .build())
            updates = await catalog_updater.get_catalog_updates(Path(path_to_catalog))
            for update in updates:
                print(update)

            return min(1, len(updates))  # Non-zero return code if we found updates
        except KatalogerException as error:
            print(f"Kataloger: {error.message}", file=sys.stderr)
            return 1

    return asyncio.run(async_main())


if __name__ == "__main__":
    sys.exit(main())
