from typing import Optional

from kataloger.data.artifact_metadata import ArtifactMetadata
from kataloger.helpers.xml_parse_helpers import try_parse_maven_group_metadata


class TestXmlParseHelpers:

    default_latest_version: str = "1.1.0"
    default_release_version: str = "1.0.0"
    default_last_updated: int = 2024

    def test_should_parse_artifact_metadata(self):
        response: str = self._create_xml_response(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_parse_metadata_with_absent_latest_version_using_last_version_as_latest_version(self):
        response: str = self._create_xml_response(
            latest_version=None,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_parse_metadata_with_absent_release_version_using_last_version_as_release_version(self):
        response: str = self._create_xml_response(
            latest_version=self.default_latest_version,
            release_version=None,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_latest_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_parse_metadata_with_only_one_version(self):
        response: str = self._create_xml_response(
            latest_version=self.default_latest_version,
            release_version=self.default_latest_version,
            versions=[self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_latest_version,
            versions=[self.default_latest_version],
            last_updated=self.default_last_updated,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_parse_metadata_with_absent_last_updated_element_using_zero_as_last_updated(self):
        response: str = self._create_xml_response(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=None,
        )
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[self.default_release_version, self.default_latest_version],
            last_updated=0,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_parse_metadata_with_absent_schema_tag(self):
        response: str = f"""\
            <metadata>
            <groupId>com.library</groupId>
            <artifactId>artifact-id</artifactId>
            <versioning>
                <versions>
                    <version>{self.default_latest_version}</version>
                </versions>
            </versioning>
            </metadata>
        """
        expected_metadata: ArtifactMetadata = ArtifactMetadata(
            latest_version=self.default_latest_version,
            release_version=self.default_latest_version,
            versions=[self.default_latest_version],
            last_updated=0,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata == expected_metadata

    def test_should_return_none_when_metadata_has_empty_versions_tag(self):
        response: str = self._create_xml_response(
            latest_version=self.default_latest_version,
            release_version=self.default_release_version,
            versions=[],
            last_updated=self.default_last_updated,
        )
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata is None

    def test_should_return_none_when_metadata_has_empty_versioning_tag(self):
        response: str = """\
            <?xml version="1.0" encoding="UTF-8"?>
            <metadata>
            <groupId>com.library</groupId>
            <artifactId>artifact-id</artifactId>
            <versioning></versioning>
            </metadata>
        """
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata is None

    def test_should_return_none_when_metadata_has_no_versioning_tag(self):
        response: str = """\
            <?xml version="1.0" encoding="UTF-8"?>
            <metadata>
            <groupId>com.library</groupId>
            <artifactId>artifact-id</artifactId>
            </metadata>
        """
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata is None

    def test_should_return_none_when_response_has_not_metadata_xml(self):
        response: str = """\
            <?xml version="1.0" encoding="UTF-8"?>
            <note>
            <script/>
            <to>Tove</to>
            <from>Jani</from>
            <heading>Reminder</heading>
            <body>Don't forget me this weekend!</body>
            </note>
        """
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata is None

    def test_should_return_none_when_response_is_not_xml(self):
        response: str = """
            fun main() {
                val name = "stranger"
                println("Hi, $name!")
                print("Current count:")
                for (i in 0..10) {
                    print(" $i")
                }
            }
        """
        actual_metadata: Optional[ArtifactMetadata] = try_parse_maven_group_metadata(response)

        assert actual_metadata is None

    @staticmethod
    def _create_xml_response(
        latest_version: Optional[str],
        release_version: Optional[str],
        versions: list[str],
        last_updated: Optional[int],
    ) -> str:
        latest_version_element = f"<latest>{latest_version}</latest>" if latest_version else ""
        release_version_element = f"<release>{release_version}</release>" if release_version else ""
        last_updated_tag = f"<lastUpdated>{last_updated}</lastUpdated>" if last_updated else ""

        versions_array = "".join(f"<version>{version}</version>" for version in versions)
        return f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <metadata>
            <groupId>com.library</groupId>
            <artifactId>artifact-id</artifactId>
            <versioning>
                {latest_version_element}
                {release_version_element}
                <versions>{versions_array}</versions>
                {last_updated_tag}
            </versioning>
            </metadata>
        """
