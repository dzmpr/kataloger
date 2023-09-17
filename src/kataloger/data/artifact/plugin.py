from kataloger.data.artifact.artifact import Artifact


class Plugin(Artifact):
    def __init__(self, name: str, coordinates: str, version: str):
        super().__init__(name, coordinates, version)

    def to_path(self) -> str:
        return f"{self.coordinates.replace('.', '/')}/{self.coordinates}.gradle.plugin"
