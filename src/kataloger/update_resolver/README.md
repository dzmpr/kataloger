## Using kataloger in own scripts

Kataloger can be used to implement your own update checking logic, but it still takes all work for gathering updates info.

### Code structure

Kataloger splits code responsibility for gathering updates info and code that searches for updates. Usually you don't need to modify code that fetches and parses maven metadata from the repository.
But it's predictable that kataloger can't cover all you need in update resolution logic. 

To address this problem [`UpdateResolver`](./base/update_resolver.py) were introduced. `UpdateResolver` is an abstract class, that should implement a single `resolve` method. 
This method gets info about artifact and artifact metadata and should return [`UpdateResolution`](./base/update_resolution.py).
`UpdateResolution` tells kataloger that there are no updates for artifact, update was found, or this resolver can't handle given artifact.
So all you need to implement custom logic is to write the own `UpdateResolver` class.

#### Example UpdateResolver

Let's imagine we want to eagerly get artifact updates despite it stability status. `UpdateResolver` would look like this:

```python
class EagerlyUpdateResolver(UpdateResolver):

    def resolve(
        self,
        artifact: Artifact,
        repositories_metadata: list[MetadataRepositoryInfo],
    ) -> tuple[UpdateResolution, Optional[ArtifactUpdate]]:
        current_version = artifact.version
        most_recently_updated_repo = max(repositories_metadata, key=lambda rm: rm.metadata.last_updated)
        if most_recently_updated_repo.metadata.latest_version == current_version:
            return UpdateResolution.UPDATE_FOUND, ArtifactUpdate(...)
        
        return UpdateResolution.NO_UPDATES, None
```

Then we need to build an instance of [`CatalogUpdater`](../catalog_updater.py) with this resolver:

```python
catalog_updater = (CatalogUpdaterBuilder()
                   .add_resolver(EagerlyUpdateResolver())
                   .build())
```

### Special version notation

By default, kataloger uses [`UniversalCatalogUpdater`](./universal/universal_update_resolver.py) that responsible for update resolution.
This resolver tries to handle as much version notations as it can, such as [semantic versions](https://semver.org), semantic-like versions (with more or less digit parts) and google pre-release notations (`dev`, `alpha`, `beta`, etc.). 
In case you just need to support special notation of artifact version, you can use `UniversalUpdateResolver` with own [`VersionFactory`](./universal/version_factory.py) and then there is no need to implement own `UpdateResolver`.
`UniversalUpdateResolver` can use multiple version factories to instantiate comparable [`Version`](./universal/version.py) classes.

### Contributing

If you have a feature request or found a bug, feel free to open pull request or issue to make this tool better for everyone!
