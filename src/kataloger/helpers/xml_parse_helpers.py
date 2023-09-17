from pyexpat import ExpatError
from typing import Optional

import xmltodict

from kataloger.data.artifact_metadata import ArtifactMetadata


def try_parse_maven_group_metadata(response: str) -> Optional[ArtifactMetadata]:
    try:
        metadata = xmltodict.parse(response)
    except ExpatError:
        return None

    try:
        version_info = metadata["metadata"]["versioning"]
        return ArtifactMetadata(
            latest_version=version_info["latest"],
            release_version=version_info["release"],
            versions=version_info["versions"]["version"],
            last_updated=int(version_info["lastUpdated"]),
        )
    except KeyError:
        return None
