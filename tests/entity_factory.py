from yarl import URL

from kataloger.data.artifact.library import Library
from kataloger.data.artifact.plugin import Plugin
from kataloger.data.artifact_update import ArtifactUpdate
from kataloger.data.repository import Repository


class EntityFactory:
    @staticmethod
    def create_repository(
        name: str = "default_repository",
        address: URL = "https://reposito.ry/",
        user: str | None = None,
        password: str | None = None,
    ) -> Repository:
        return Repository(
            name=name,
            address=address,
            user=user,
            password=password,
        )

    @staticmethod
    def create_library(
        name: str = "default_library",
        coordinates: str = "com.library.group:library",
        version: str = "1.0.0",
    ) -> Library:
        return Library(
            name=name,
            coordinates=coordinates,
            version=version,
        )

    @staticmethod
    def create_plugin(
        name: str = "default_plugin",
        coordinates: str = "com.library.group:library",
        version: str = "1.0.0",
    ) -> Plugin:
        return Plugin(
            name=name,
            coordinates=coordinates,
            version=version,
        )

    @staticmethod
    def create_artifact_update(
        name: str = "artifact_name",
        update_repository_name: str = "update_repository_name",
        current_version: str = "0.1.0",
        available_version: str = "1.0.0",
    ) -> ArtifactUpdate:
        return ArtifactUpdate(
            name=name,
            update_repository_name=update_repository_name,
            current_version=current_version,
            available_version=available_version,
        )
