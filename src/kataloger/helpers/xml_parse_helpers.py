from pyexpat import ExpatError
from typing import Optional

import xmltodict

from kataloger.data.artifact_metadata import ArtifactMetadata


def try_parse_maven_group_metadata(response: str) -> Optional[ArtifactMetadata]:
    try:
        metadata = xmltodict.parse(response.strip())
    except ExpatError:
        return None

    try:
        version_info = metadata["metadata"]["versioning"]
        versions = version_info["versions"]["version"]
        if not isinstance(versions, list):
            versions = [versions]

        return ArtifactMetadata(
            latest_version=version_info.get("latest", versions[-1]),
            release_version=version_info.get("release", versions[-1]),
            versions=versions,
            last_updated=int(version_info.get("lastUpdated", 0)),
        )
    except (KeyError, TypeError):
        return None
