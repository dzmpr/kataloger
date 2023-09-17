from kataloger.data.artifact.artifact import Artifact


class Library(Artifact):
    def __init__(self, name: str, coordinates: str, version: str):
        super().__init__(name, coordinates, version)

    def to_path(self) -> str:
        return self.coordinates.replace(".", "/").replace(":", "/")
